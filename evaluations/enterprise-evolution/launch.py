"""Launch a supervised native phase with repository-local caches and exact argv."""
import argparse
import os
import subprocess
import sys

from prepare import WORK, HERE, HPY, posix


def launch(phase):
    cache = WORK / "host-cache"
    for name in ("tmp", "uv", "xdg"):
        (cache / name).mkdir(parents=True, exist_ok=True)
    args = {"development": [posix(HERE / "run.py")], "validation": [posix(HERE / "finalize.py"), "run-gate"], "normalize": [posix(HERE / "report.py"), "normalize"]}[phase]
    command = ["env", "PYTHONDONTWRITEBYTECODE=1", "PYTHONPATH="+posix(WORK)+":"+posix(HERE), "TMPDIR="+posix(cache / "tmp"), "UV_CACHE_DIR="+posix(cache / "uv"), "XDG_CACHE_HOME="+posix(cache / "xdg"), "HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1", "OMP_NUM_THREADS=2", "MKL_NUM_THREADS=2", "OPENBLAS_NUM_THREADS=2", HPY, "-B", *args]
    log = WORK / "logs" / (phase+"-live-001.log")
    with log.open("xb") as stream:
        result = subprocess.run((["wsl", "-d", "Ubuntu", "--exec"] if os.name == "nt" else [])+command, stdout=stream, stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise RuntimeError("Preserve the failed phase and inspect " + str(log))
    print(phase + " completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["development", "validation", "normalize"])
    launch(parser.parse_args().phase)
