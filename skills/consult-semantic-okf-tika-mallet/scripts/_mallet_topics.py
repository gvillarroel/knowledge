#!/usr/bin/env python3
"""Retrain Java MALLET topics in disposable storage for deep validation."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import zipfile
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable, Iterator, Mapping, Sequence

from _safe_paths import (
    UnsafePathError,
    file_identity,
    lexical_absolute,
    reject_overlaps,
    require_identity,
    require_real_directory,
    require_regular_file,
    scan_regular_tree,
)


MALLET_VERSION = "2.1.0"
MALLET_ALGORITHM = "mallet-2.1.0-parallel-topic-model-v1"


class MalletRuntimeError(RuntimeError):
    """Report a Java runtime, MALLET output, or deterministic-model failure."""


@dataclass(frozen=True)
class MalletRuntime:
    """Describe the exact external runtime used for deep topic validation."""

    java: Path
    java_version: str
    mallet_home: Path
    mallet_version: str
    jar_inventory: tuple[dict[str, str], ...]
    jar_tree_sha256: str
    java_identity: tuple[int, int] | None = None
    home_identity: tuple[int, int] | None = None

    def payload(self) -> dict[str, Any]:
        """Return the path-independent projection binding."""

        return {
            "java_version": self.java_version,
            "mallet_jar_inventory": list(self.jar_inventory),
            "mallet_jar_tree_sha256": self.jar_tree_sha256,
            "mallet_version": self.mallet_version,
        }


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _run_java(
    command: Sequence[str], *, cwd: Path, timeout: int, label: str
) -> tuple[str, str, int]:
    try:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MalletRuntimeError(f"{label} failed to execute: {exc}") from exc
    try:
        stdout = completed.stdout.decode("utf-8", errors="strict")
        stderr = completed.stderr.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise MalletRuntimeError(f"{label} did not emit valid UTF-8") from exc
    return (
        stdout.replace("\r\n", "\n").replace("\r", "\n"),
        stderr.replace("\r\n", "\n").replace("\r", "\n"),
        completed.returncode,
    )


def preflight_mallet(java: Path, mallet_home: Path) -> MalletRuntime:
    """Require Java 17+ and the exact MALLET 2.1.0 binary layout."""

    try:
        java_path = require_regular_file(java, label="Java executable")
        home = require_real_directory(mallet_home, label="MALLET home")
    except UnsafePathError as exc:
        raise MalletRuntimeError(str(exc)) from exc
    library = home / "lib"
    main_jar = library / "mallet-2.1.0.jar"
    inventory, inventory_sha256 = _mallet_inventory(home)
    try:
        main_jar = require_regular_file(main_jar, label="MALLET main jar")
    except UnsafePathError as exc:
        raise MalletRuntimeError(str(exc)) from exc
    stdout, stderr, returncode = _run_java(
        [str(java_path), "-version"], cwd=home, timeout=60, label="Java preflight"
    )
    if returncode != 0:
        raise MalletRuntimeError("Java preflight failed")
    java_version = (stdout or stderr).strip()
    match = re.search(r'version "(\d+)(?:\.|\")', java_version)
    if not match or int(match.group(1)) < 17:
        raise MalletRuntimeError("Java 17 or later is required")
    try:
        with zipfile.ZipFile(main_jar) as archive:
            names = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        raise MalletRuntimeError(f"MALLET main jar is unreadable: {exc}") from exc
    required_classes = {
        "cc/mallet/classify/tui/Csv2Vectors.class",
        "cc/mallet/topics/tui/TopicTrainer.class",
        "cc/mallet/topics/ParallelTopicModel.class",
    }
    if not required_classes.issubset(names):
        raise MalletRuntimeError("MALLET main jar lacks required classes")
    return MalletRuntime(
        java=java_path,
        java_version=java_version,
        mallet_home=home,
        mallet_version=MALLET_VERSION,
        jar_inventory=inventory,
        jar_tree_sha256=inventory_sha256,
        java_identity=file_identity(java_path),
        home_identity=file_identity(home),
    )


def _mallet_inventory(home: Path) -> tuple[tuple[dict[str, str], ...], str]:
    """Bind exactly the closed, immediate MALLET lib jar classpath."""

    library = home / "lib"
    try:
        files, directories = scan_regular_tree(library, label="MALLET lib directory")
    except UnsafePathError as exc:
        raise MalletRuntimeError(str(exc)) from exc
    if directories or any(path.parent != library for path in files):
        raise MalletRuntimeError("MALLET lib must contain only immediate jar files")
    if any(path.suffix.casefold() != ".jar" for path in files):
        raise MalletRuntimeError("MALLET lib contains a non-jar classpath entry")
    rows = tuple(
        {
            "path": path.relative_to(home).as_posix(),
            "sha256": _sha256_file(path),
        }
        for path in files
    )
    if not rows or not any(row["path"] == "lib/mallet-2.1.0.jar" for row in rows):
        raise MalletRuntimeError("MALLET jar inventory is incomplete")
    return rows, _sha256_json(list(rows))


def _verify_runtime(runtime: MalletRuntime) -> None:
    """Reject executable identity or classpath changes after preflight."""

    if runtime.java_identity is None or runtime.home_identity is None:
        return
    try:
        require_identity(runtime.java, runtime.java_identity, label="Java executable")
        require_identity(runtime.mallet_home, runtime.home_identity, label="MALLET home")
    except UnsafePathError as exc:
        raise MalletRuntimeError(str(exc)) from exc
    inventory, tree_sha256 = _mallet_inventory(runtime.mallet_home)
    if inventory != runtime.jar_inventory or tree_sha256 != runtime.jar_tree_sha256:
        raise MalletRuntimeError("MALLET jar classpath changed after preflight")


def validate_toolchain(value: Any) -> dict[str, Any]:
    """Validate a stored path-independent MALLET runtime binding."""

    if not isinstance(value, dict) or set(value) != {
        "java_version",
        "mallet_jar_inventory",
        "mallet_jar_tree_sha256",
        "mallet_version",
    }:
        raise MalletRuntimeError("MALLET toolchain binding has an invalid schema")
    if value["mallet_version"] != MALLET_VERSION:
        raise MalletRuntimeError("MALLET toolchain version is unsupported")
    if (
        not isinstance(value["java_version"], str)
        or not (match := re.search(r'version "(\d+)', value["java_version"]))
        or int(match.group(1)) < 17
    ):
        raise MalletRuntimeError("MALLET Java version binding is invalid")
    jars = value["mallet_jar_inventory"]
    if (
        not isinstance(jars, list)
        or not jars
        or any(
            not isinstance(row, dict)
            or set(row) != {"path", "sha256"}
            or not isinstance(row["path"], str)
            or "\\" in row["path"]
            or PureWindowsPath(row["path"]).drive
            or PurePosixPath(row["path"]).is_absolute()
            or any(part in {"", ".", ".."} for part in PurePosixPath(row["path"]).parts)
            or not re.fullmatch(r"[0-9a-f]{64}", str(row["sha256"]))
            for row in jars
        )
    ):
        raise MalletRuntimeError("MALLET jar inventory is malformed")
    if (
        jars != sorted(jars, key=lambda row: row["path"])
        or len({row["path"].casefold() for row in jars}) != len(jars)
    ):
        raise MalletRuntimeError("MALLET jar inventory must be sorted and unique")
    if not any(row["path"] == "lib/mallet-2.1.0.jar" for row in jars):
        raise MalletRuntimeError("MALLET jar inventory lacks the main 2.1.0 jar")
    if value["mallet_jar_tree_sha256"] != _sha256_json(jars):
        raise MalletRuntimeError("MALLET jar inventory digest is stale")
    return json.loads(_canonical_json(value))


def _command(runtime: MalletRuntime, class_name: str) -> list[str]:
    classpath: list[str] = []
    for row in runtime.jar_inventory:
        value = str(row["path"])
        relative = PurePosixPath(value)
        if (
            "\\" in value
            or relative.is_absolute()
            or not relative.parts
            or any(part in {"", ".", ".."} for part in relative.parts)
        ):
            raise MalletRuntimeError("MALLET jar inventory contains an unsafe path")
        classpath.append(str(runtime.mallet_home.joinpath(*relative.parts)))
    if not classpath:
        raise MalletRuntimeError("MALLET classpath is empty")
    return [
        str(runtime.java),
        "-Xmx1G",
        "-ea",
        "-Dfile.encoding=UTF-8",
        "-Duser.language=en",
        "-Duser.country=US",
        "-Duser.timezone=UTC",
        "-classpath",
        os.pathsep.join(classpath),
        class_name,
    ]


def _require_run(
    command: Sequence[str],
    *,
    runtime: MalletRuntime,
    timeout: int,
    label: str,
) -> None:
    for attempt in range(2):
        _verify_runtime(runtime)
        stdout, stderr, returncode = _run_java(
            command, cwd=runtime.mallet_home, timeout=timeout, label=label
        )
        combined = f"{stdout}\n{stderr}"
        transient_jshell = (
            returncode != 0
            and "Launching JShell execution engine threw" in combined
            and "TransportTimeoutException: timeout waiting for connection" in combined
        )
        if transient_jshell and attempt == 0:
            continue
        break
    _verify_runtime(runtime)
    if returncode != 0:
        raise MalletRuntimeError(
            f"{label} exited {returncode}: {(stderr or stdout).strip()[:1000]}"
        )
    for marker in (
        "Missing argument for option",
        "Unrecognized option",
        "Exception in thread",
        "CommandOption$IllegalArgumentException",
    ):
        if marker in combined:
            raise MalletRuntimeError(f"{label} reported an error: {marker}")


def _require_output(path: Path, label: str) -> None:
    try:
        checked = require_regular_file(path, label=label)
    except UnsafePathError as exc:
        raise MalletRuntimeError(str(exc)) from exc
    if checked.stat().st_size == 0:
        raise MalletRuntimeError(f"MALLET did not create a non-empty {label}")


@contextmanager
def _private_scratch(forbidden_roots: Sequence[Path]) -> Iterator[Path]:
    """Create scratch outside the bundle and runtime trees, even if TEMP is hostile."""

    try:
        base = require_real_directory(Path(tempfile.gettempdir()), label="temporary root")
        for forbidden in forbidden_roots:
            forbidden_absolute = lexical_absolute(forbidden)
            try:
                base.relative_to(forbidden_absolute)
            except ValueError:
                continue
            raise UnsafePathError(
                f"temporary root is inside forbidden root: {forbidden_absolute}"
            )
        with tempfile.TemporaryDirectory(
            prefix="semantic-okf-mallet-consult-", dir=base
        ) as temporary:
            work = require_real_directory(Path(temporary), label="MALLET scratch")
            reject_overlaps(work, forbidden_roots, label="MALLET scratch")
            yield work
    except UnsafePathError as exc:
        raise MalletRuntimeError(str(exc)) from exc


def _filtered_corpus(
    documents: Sequence[Mapping[str, Any]],
    plan: Mapping[str, Any],
    unigrams: Callable[[str, Mapping[str, Any]], list[str]],
) -> tuple[list[list[str]], list[str]]:
    config = plan["topics"]
    rows = [
        unigrams(str(document["title"]), plan)
        + unigrams(str(document["text"]), plan)
        for document in documents
    ]
    frequencies = Counter(term for row in rows for term in set(row))
    maximum = len(documents) * float(config["max_document_fraction"])
    vocabulary = sorted(
        term
        for term, frequency in frequencies.items()
        if frequency >= config["min_document_frequency"]
        and frequency <= maximum + 1e-12
    )
    allowed = set(vocabulary)
    filtered = [[term for term in row if term in allowed] for row in rows]
    if not vocabulary or any(not row for row in filtered):
        raise MalletRuntimeError("MALLET vocabulary filtering removed required text")
    return filtered, vocabulary


def _parse_doc_topics(
    path: Path, document_ids: Sequence[str], topic_count: int
) -> list[list[float]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != len(document_ids):
        raise MalletRuntimeError("MALLET document-topic output is incomplete")
    result: list[list[float]] = []
    for expected, (line, document_id) in enumerate(zip(lines, document_ids)):
        fields = line.split("\t")
        if len(fields) != topic_count + 2:
            raise MalletRuntimeError("MALLET document-topic row width is invalid")
        try:
            index = int(fields[0])
            weights = [float(value) for value in fields[2:]]
        except ValueError as exc:
            raise MalletRuntimeError("MALLET document-topic row is malformed") from exc
        if index != expected or fields[1] != document_id:
            raise MalletRuntimeError("MALLET document order or identity changed")
        if any(not math.isfinite(value) or value < 0.0 for value in weights):
            raise MalletRuntimeError("MALLET document-topic weight is invalid")
        if not math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-7):
            raise MalletRuntimeError("MALLET document-topic weights do not sum to one")
        result.append(weights)
    return result


def _parse_topic_keys(path: Path, topic_count: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != topic_count:
        raise MalletRuntimeError("MALLET topic-key output is incomplete")
    for expected, line in enumerate(lines):
        fields = line.split("\t")
        try:
            index = int(fields[0])
            alpha = float(fields[1])
        except (IndexError, ValueError) as exc:
            raise MalletRuntimeError("MALLET topic-key output is malformed") from exc
        if index != expected or not math.isfinite(alpha) or alpha <= 0.0:
            raise MalletRuntimeError("MALLET topic-key identity or alpha is invalid")


def _parse_counts(
    path: Path, vocabulary: Sequence[str], topic_count: int
) -> dict[str, dict[str, int]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != len(vocabulary):
        raise MalletRuntimeError("MALLET word-topic output is incomplete")
    result: dict[str, dict[str, int]] = {}
    for expected, line in enumerate(lines):
        fields = line.split()
        if len(fields) < 2:
            raise MalletRuntimeError("MALLET word-topic row is malformed")
        try:
            index = int(fields[0])
        except ValueError as exc:
            raise MalletRuntimeError("MALLET word-topic index is malformed") from exc
        if index != expected:
            raise MalletRuntimeError("MALLET word-topic indices are not contiguous")
        term = fields[1]
        counts: dict[str, int] = {}
        for assignment in fields[2:]:
            try:
                topic_raw, count_raw = assignment.split(":", 1)
                topic = int(topic_raw)
                count = int(count_raw)
            except ValueError as exc:
                raise MalletRuntimeError("MALLET word-topic assignment is malformed") from exc
            if not 0 <= topic < topic_count or count <= 0 or str(topic) in counts:
                raise MalletRuntimeError("MALLET word-topic assignment is invalid")
            counts[str(topic)] = count
        if term in result:
            raise MalletRuntimeError("MALLET vocabulary contains a duplicate term")
        result[term] = counts
    if set(result) != set(vocabulary):
        raise MalletRuntimeError("MALLET returned a foreign vocabulary")
    return result


def _parse_weights(
    path: Path,
    vocabulary: Sequence[str],
    topic_count: int,
    beta: float,
    counts: Mapping[str, Mapping[str, int]],
) -> list[list[float]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != topic_count * len(vocabulary):
        raise MalletRuntimeError("MALLET topic-word output is incomplete")
    allowed = set(vocabulary)
    by_topic = [dict() for _ in range(topic_count)]
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 3:
            raise MalletRuntimeError("MALLET topic-word row is malformed")
        try:
            topic = int(fields[0])
            weight = float(fields[2])
        except ValueError as exc:
            raise MalletRuntimeError("MALLET topic-word value is malformed") from exc
        term = fields[1]
        if (
            not 0 <= topic < topic_count
            or term not in allowed
            or term in by_topic[topic]
            or not math.isfinite(weight)
            or weight <= 0.0
        ):
            raise MalletRuntimeError("MALLET topic-word identity or weight is invalid")
        by_topic[topic][term] = weight
    probabilities: list[list[float]] = []
    for topic, weights in enumerate(by_topic):
        if set(weights) != allowed:
            raise MalletRuntimeError("MALLET topic-word coverage is incomplete")
        ordered: list[float] = []
        for term in vocabulary:
            weight = weights[term]
            expected = float(counts[term].get(str(topic), 0)) + beta
            if not math.isclose(weight, expected, rel_tol=0.0, abs_tol=1e-9):
                raise MalletRuntimeError("MALLET topic-word weight disagrees with counts")
            ordered.append(weight)
        total = sum(ordered)
        probabilities.append([weight / total for weight in ordered])
    return probabilities


def derive_topics(
    documents: list[dict[str, Any]],
    plan: Mapping[str, Any],
    runtime: MalletRuntime,
    unigrams: Callable[[str, Mapping[str, Any]], list[str]],
    *,
    forbidden_roots: Sequence[Path] = (),
) -> dict[str, Any]:
    """Retrain the canonical fixed-seed one-thread Java MALLET projection."""

    config = plan["topics"]
    corpus_rows, vocabulary = _filtered_corpus(documents, plan, unigrams)
    document_ids = [str(document["document_id"]) for document in documents]
    if any("\t" in value or "\n" in value or "\r" in value for value in document_ids):
        raise MalletRuntimeError("document identifiers are unsafe for MALLET")
    timeout = int(config["timeout_seconds"])
    with _private_scratch(forbidden_roots) as work:
        corpus_tsv = work / "corpus.tsv"
        corpus_tsv.write_text(
            "".join(
                f"{document_id}\tX\t{' '.join(tokens)}\n"
                for document_id, tokens in zip(document_ids, corpus_rows)
            ),
            encoding="utf-8",
            newline="\n",
        )
        corpus = work / "corpus.mallet"
        _require_run(
            [
                *_command(runtime, "cc.mallet.classify.tui.Csv2Vectors"),
                "--input",
                str(corpus_tsv),
                "--output",
                str(corpus),
                "--keep-sequence",
                "TRUE",
                "--line-regex",
                r"^([^\t]+)\t([^\t]+)\t(.*)$",
                "--name",
                "1",
                "--label",
                "2",
                "--data",
                "3",
                "--token-regex",
                "[a-z0-9]+",
                "--preserve-case",
                "TRUE",
                "--remove-stopwords",
                "FALSE",
            ],
            runtime=runtime,
            timeout=timeout,
            label="MALLET import-file",
        )
        _require_output(corpus, "serialized corpus")
        topic_keys = work / "topic-keys.txt"
        doc_topics = work / "doc-topics.txt"
        topic_words = work / "topic-word-weights.txt"
        word_topics = work / "word-topic-counts.txt"
        _require_run(
            [
                *_command(runtime, "cc.mallet.topics.tui.TopicTrainer"),
                "--input",
                str(corpus),
                "--num-topics",
                str(config["topic_count"]),
                "--num-threads",
                "1",
                "--num-iterations",
                str(config["num_iterations"]),
                "--num-icm-iterations",
                str(config["num_icm_iterations"]),
                "--random-seed",
                str(config["random_seed"]),
                "--optimize-interval",
                str(config["optimize_interval"]),
                "--optimize-burn-in",
                str(config["optimize_burn_in"]),
                "--alpha",
                str(config["alpha_sum"]),
                "--beta",
                str(config["beta"]),
                "--num-top-words",
                str(config["top_terms"]),
                "--show-topics-interval",
                "0",
                "--output-topic-keys",
                str(topic_keys),
                "--output-doc-topics",
                str(doc_topics),
                "--doc-topics-threshold",
                "0.0",
                "--topic-word-weights-file",
                str(topic_words),
                "--word-topic-counts-file",
                str(word_topics),
            ],
            runtime=runtime,
            timeout=timeout,
            label="MALLET train-topics",
        )
        for path, label in (
            (topic_keys, "topic keys"),
            (doc_topics, "document topics"),
            (topic_words, "topic-word weights"),
            (word_topics, "word-topic counts"),
        ):
            _require_output(path, label)
        _parse_topic_keys(topic_keys, int(config["topic_count"]))
        counts = _parse_counts(word_topics, vocabulary, int(config["topic_count"]))
        topic_word = _parse_weights(
            topic_words,
            vocabulary,
            int(config["topic_count"]),
            float(config["beta"]),
            counts,
        )
        document_topics = _parse_doc_topics(
            doc_topics, document_ids, int(config["topic_count"])
        )
    labels = {
        term: max(
            range(len(topic_word)),
            key=lambda topic: (topic_word[topic][term_index], -topic),
        )
        for term_index, term in enumerate(vocabulary)
    }
    topics: list[dict[str, Any]] = []
    for topic_index, probabilities in enumerate(topic_word):
        ranked = sorted(
            zip(probabilities, vocabulary), key=lambda item: (-item[0], item[1])
        )
        topics.append(
            {
                "topic_id": f"topic-{topic_index:02d}",
                "seed": ranked[0][1],
                "term_count": sum(1 for value in labels.values() if value == topic_index),
                "terms": [
                    {"term": term, "weight": round(probability, 8)}
                    for probability, term in ranked[: int(config["top_terms"])]
                    if probability > 0.0
                ],
            }
        )
    for document, weights in zip(documents, document_topics):
        document["topic_weights"] = [
            {"topic_id": f"topic-{index:02d}", "weight": round(weight, 8)}
            for index, weight in enumerate(weights)
            if weight > 0.0
        ]
    return {
        "schema_version": "1.0",
        "algorithm": MALLET_ALGORITHM,
        "requested_topic_count": config["topic_count"],
        "topic_count": len(topics),
        "iterations": config["num_iterations"],
        "term_topics": [
            {"term": term, "topic_id": f"topic-{labels[term]:02d}"}
            for term in sorted(labels)
        ],
        "topics": topics,
    }
