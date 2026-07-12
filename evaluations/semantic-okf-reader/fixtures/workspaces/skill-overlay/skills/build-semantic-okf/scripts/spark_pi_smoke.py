#!/usr/bin/env python3
"""Prove real PySpark execution with a deterministic distributed Pi estimate."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys


def build_parser() -> argparse.ArgumentParser:
    """Build the Spark Pi command-line parser."""

    parser = argparse.ArgumentParser(description="Run a deterministic distributed Spark Pi smoke test.")
    parser.add_argument("--master", default="local[2]")
    parser.add_argument("--partitions", type=int, default=2)
    parser.add_argument("--samples", type=int, default=100_000)
    parser.add_argument("--tolerance", type=float, default=0.001)
    return parser


def estimate_pi(master: str, partitions: int, samples: int) -> dict[str, object]:
    """Estimate Pi by midpoint integration over a partitioned Spark DataFrame."""

    if partitions < 2:
        raise ValueError("--partitions must be at least 2 to test distributed execution")
    if samples < partitions:
        raise ValueError("--samples must be at least the partition count")
    try:
        from pyspark.sql import SparkSession, functions as F
    except ImportError as exc:
        raise RuntimeError("PySpark is missing; install scripts/requirements.txt") from exc

    builder = (
        SparkSession.builder.master(master)
        .appName("semantic-okf-spark-pi")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", str(partitions))
    )
    if master.startswith("local"):
        os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
        os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
        os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
        builder = builder.config("spark.driver.host", "127.0.0.1").config(
            "spark.driver.bindAddress", "127.0.0.1"
        )
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    try:
        points = spark.range(0, samples, 1, partitions)
        x = (F.col("id").cast("double") + F.lit(0.5)) / F.lit(float(samples))
        estimate = points.select((F.lit(4.0) / (F.lit(1.0) + x * x)).alias("term")).agg(
            (F.sum("term") / F.lit(float(samples))).alias("pi")
        ).first()["pi"]
        return {
            "spark_version": spark.version,
            "master": spark.sparkContext.master,
            "partitions": points.rdd.getNumPartitions(),
            "samples": samples,
            "pi": float(estimate),
            "absolute_error": abs(float(estimate) - math.pi),
        }
    finally:
        spark.stop()


def main(argv: list[str] | None = None) -> int:
    """Run the Spark Pi smoke test and emit one JSON document."""

    args = build_parser().parse_args(argv)
    try:
        result = estimate_pi(args.master, args.partitions, args.samples)
    except Exception as exc:
        module = type(exc).__module__
        if not isinstance(exc, (RuntimeError, ValueError)) and not module.startswith(("pyspark", "py4j")):
            raise
        code = "input-error" if isinstance(exc, ValueError) else "processor-failure"
        print(json.dumps({"status": "error", "code": code, "error": str(exc)}, sort_keys=True))
        return 2
    result["status"] = "pass" if result["absolute_error"] <= args.tolerance else "fail"
    result["tolerance"] = args.tolerance
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
