ARG PYTHON_IMAGE=python:3.12.13-slim-bookworm@sha256:d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b
FROM ${PYTHON_IMAGE}

ENV HF_HUB_OFFLINE=1 \
    HF_HOME=/models/huggingface \
    HF_HUB_CACHE=/models/huggingface/hub \
    NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_FUND=false \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SENTENCE_TRANSFORMERS_HOME=/models/huggingface \
    SEMANTIC_OKF_HF_HUB_CACHE=/models/huggingface/hub \
    TOKENIZERS_PARALLELISM=false \
    TRANSFORMERS_OFFLINE=1

LABEL org.opencontainers.image.title="Semantic OKF Harbor pinned runtime" \
      org.opencontainers.image.version="2.0" \
      org.semantic-okf.python.version="3.12.13" \
      org.semantic-okf.node.version="22.23.1" \
      org.semantic-okf.npm.version="10.9.8" \
      org.semantic-okf.pi-coding-agent.version="0.73.1"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates \
        curl \
        git \
        jq \
        procps \
        ripgrep \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    test "$(dpkg --print-architecture)" = "amd64"; \
    node_archive="node-v22.23.1-linux-x64.tar.xz"; \
    curl --fail --location --show-error --silent \
        "https://nodejs.org/dist/v22.23.1/${node_archive}" \
        --output "/tmp/${node_archive}"; \
    printf '%s  %s\n' \
        '9749e988f437343b7fa832c69ded82a312e41a03116d766797ac14f6f9eee578' \
        "/tmp/${node_archive}" \
        | sha256sum --check --strict -; \
    tar --extract --xz --file "/tmp/${node_archive}" \
        --directory /usr/local --strip-components=1; \
    rm "/tmp/${node_archive}"; \
    test "$(node --version)" = "v22.23.1"; \
    test "$(npm --version)" = "10.9.8"

COPY requirements.txt /tmp/semantic-okf-harbor-requirements.txt
RUN python -m pip install --no-cache-dir \
        -r /tmp/semantic-okf-harbor-requirements.txt \
    && rm /tmp/semantic-okf-harbor-requirements.txt \
    && test "$(python -c 'import platform; print(platform.python_version())')" = "3.12.13"

WORKDIR /opt/semantic-okf/pi-coding-agent
COPY pinned/package.json pinned/package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund \
    && test "$(node -p 'require("./node_modules/@mariozechner/pi-coding-agent/package.json").version')" = "0.73.1" \
    && test -x node_modules/.bin/pi \
    && ln --symbolic /opt/semantic-okf/pi-coding-agent/node_modules/.bin/pi /usr/local/bin/pi \
    && npm cache clean --force

RUN mkdir -p /knowledge /models/huggingface/hub /workspace /root/.pi/agent \
    && : > /root/.pi/agent/auth.json \
    && chmod 0600 /root/.pi/agent/auth.json

WORKDIR /workspace
