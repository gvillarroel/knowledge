from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "evaluations/semantic-okf-tika-mallet-tantivy/runtime"


def test_runtime_pins_linux_jdk_and_content_addressed_base() -> None:
    dockerfile = (RUNTIME / "Dockerfile").read_text(encoding="utf-8")

    assert (
        "semantic-okf-harbor-runtime:"
        "sha256-1315195dcef58980e6d2620eaa41062ea6edc15c3eb8ed47d42c143be57aded5"
        in dockerfile
    )
    assert "openjdk-17-jdk-headless=${OPENJDK_VERSION}" in dockerfile
    assert "ARG OPENJDK_VERSION=17.0.19+10-1~deb12u2" in dockerfile
    assert "JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" in dockerfile
    assert "javac" in dockerfile


def test_runtime_declares_stable_external_tool_mounts() -> None:
    dockerfile = (RUNTIME / "Dockerfile").read_text(encoding="utf-8")
    readme = (RUNTIME / "README.md").read_text(encoding="utf-8")

    assert "SEMANTIC_OKF_TIKA_HOME=/opt/semantic-okf/tika" in dockerfile
    assert "SEMANTIC_OKF_MALLET_HOME=/opt/semantic-okf/mallet" in dockerfile
    assert "read-only" in readme
