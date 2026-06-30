# Astrology Daily Quotes - GPU inference image (Gemma 4 E2B-IT + Swiss Ephemeris)
# Target hardware: AWS g6.xlarge (NVIDIA L4, Ada) - native bf16, CUDA 12.8.
# The torch+cu128 wheels bundle the CUDA libs; the cudnn-runtime base supplies cuDNN.
FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/hf_cache \
    HF_HUB_DISABLE_TELEMETRY=1

# Python 3.11 (timezonefinder 8.x requires >=3.11) + build tools (gcc for any
# triton/torch JIT) + git/curl for healthcheck. 3.11 via the deadsnakes PPA.
RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common curl ca-certificates gnupg \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3.11-venv \
        git gcc build-essential \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install torch + torchvision (cu128) FIRST from the pytorch index so the binaries
# match CUDA 12.8 (the requirements.txt pins the same versions).
RUN python -m pip install --upgrade pip \
    && python -m pip install \
        --index-url https://download.pytorch.org/whl/cu128 \
        torch==2.11.0+cu128 torchvision==0.26.0+cu128

# The rest of the deps. --extra-index-url keeps the cu128 wheels resolvable for the
# torch/torchvision pins inside requirements.txt (already satisfied above).
COPY requirements.txt .
RUN python -m pip install \
        --extra-index-url https://download.pytorch.org/whl/cu128 \
        -r requirements.txt

# Bake the Gemma model into the image for fast, reproducible cold starts (no Hub
# dependency at runtime). If the model is gated, pass a token at build time:
#   docker build --build-arg HF_TOKEN=hf_xxx ...
# (the token must have accepted the Gemma license on huggingface.co).
ARG MODEL_NAME=google/gemma-4-E2B-it
ARG HF_TOKEN=""
RUN MODEL_NAME="${MODEL_NAME}" HF_TOKEN="${HF_TOKEN}" HUGGING_FACE_HUB_TOKEN="${HF_TOKEN}" \
    python -c "import os; from huggingface_hub import snapshot_download; snapshot_download(os.environ['MODEL_NAME'], token=(os.environ.get('HF_TOKEN') or None))"

# Application code.
COPY src ./src

ENV HOST=0.0.0.0 \
    PORT=7005

EXPOSE 7005

# Model loads at import time (before uvicorn serves), so a 200 on /status means ready.
HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=5 \
    CMD curl -fsS http://localhost:7005/status || exit 1

CMD ["python", "src/main.py"]
