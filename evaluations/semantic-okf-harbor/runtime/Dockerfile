ARG PYTHON_IMAGE=python:3.12.13-slim-bookworm
FROM ${PYTHON_IMAGE}

ENV HF_HUB_OFFLINE=1 \
    HF_HOME=/models/huggingface \
    HF_HUB_CACHE=/models/huggingface/hub \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TOKENIZERS_PARALLELISM=false \
    TRANSFORMERS_OFFLINE=1 \
    SENTENCE_TRANSFORMERS_HOME=/models/huggingface \
    SEMANTIC_OKF_HF_HUB_CACHE=/models/huggingface/hub

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl git jq procps ripgrep \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/semantic-okf-harbor-requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/semantic-okf-harbor-requirements.txt \
    && rm /tmp/semantic-okf-harbor-requirements.txt

RUN mkdir -p /knowledge /models/huggingface/hub /workspace /root/.pi/agent \
    && : > /root/.pi/agent/auth.json \
    && chmod 0600 /root/.pi/agent/auth.json
WORKDIR /workspace
