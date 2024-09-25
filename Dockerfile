# syntax = docker/dockerfile:experimental
# Initialize device type args
# use build args in the docker build commmand with --build-arg="BUILDARG=true"
ARG USE_CUDA=true
ARG USE_OLLAMA=false
# Tested with cu117 for CUDA 11 and cu121 for CUDA 12 (default)
ARG USE_CUDA_VER=cu121
# any sentence transformer model; models to use can be found at https://huggingface.co/models?library=sentence-transformers
# Leaderboard: https://huggingface.co/spaces/mteb/leaderboard 
# for better performance and multilangauge support use "intfloat/multilingual-e5-large" (~2.5GB) or "intfloat/multilingual-e5-base" (~1.5GB)
# IMPORTANT: If you change the embedding model (sentence-transformers/all-MiniLM-L6-v2) and vice versa, you aren't able to use RAG Chat with your previous documents loaded in the WebUI! You need to re-embed them.
# ARG USE_EMBEDDING_MODEL=intfloat/multilingual-e5-large
# ARG USE_RERANKING_MODEL=intfloat/multilingual-e5-large
ARG USE_EMBEDDING_MODEL=BAAI/bge-m3
ARG USE_RERANKING_MODEL=BAAI/bge-m3
ARG BUILD_HASH=dev-build
# Override at your own risk - non-root configurations are untested
ARG UID=0
ARG GID=0

######## WebUI frontend ########
FROM --platform=$BUILDPLATFORM node:21-alpine3.19 as build

# 设置代理
ENV http_proxy=http://192.168.100.23:1081
ENV https_proxy=http://192.168.100.23:1081
ENV no_proxy=0.0.0.0,localhost,127.0.0.1,192.168.98.34
ARG BUILD_HASH

WORKDIR /app

COPY package.json package-lock.json ./
ENV NODE_OPTIONS=--max_old_space_size=4096
RUN npm ci

COPY . .
ENV APP_BUILD_HASH=${BUILD_HASH}
RUN npm run build

######## WebUI backend ########
FROM python:3.11-slim-bookworm as base

# Use args
ARG USE_CUDA
ARG USE_OLLAMA
ARG USE_CUDA_VER
ARG USE_EMBEDDING_MODEL
ARG USE_RERANKING_MODEL
ARG UID
ARG GID

RUN echo "The value of USE_CUDA is: ${USE_CUDA}"
RUN echo "The value of USE_OLLAMA is: ${USE_OLLAMA}"
RUN echo "The value of USE_CUDA_VER is: ${USE_CUDA_VER}"
RUN echo "The value of USE_EMBEDDING_MODEL is: ${USE_EMBEDDING_MODEL}"
RUN echo "The value of USE_RERANKING_MODEL is: ${USE_RERANKING_MODEL}"
RUN echo "The value of UID is: ${UID}"
RUN echo "The value of GID is: ${GID}"

## Basis ##
ENV ENV=prod \
    PORT=8080 \
    # pass build args to the build
    USE_OLLAMA_DOCKER=${USE_OLLAMA} \
    USE_CUDA_DOCKER=${USE_CUDA} \
    USE_CUDA_DOCKER_VER=${USE_CUDA_VER} \
    USE_EMBEDDING_MODEL_DOCKER=${USE_EMBEDDING_MODEL} \
    USE_RERANKING_MODEL_DOCKER=${USE_RERANKING_MODEL}

## Basis URL Config ##
ENV OLLAMA_BASE_URL="/ollama" \
    OPENAI_API_BASE_URL=""

## API Key and Security Config ##
ENV OPENAI_API_KEY="" \
    WEBUI_SECRET_KEY="" \
    SCARF_NO_ANALYTICS=true \
    DO_NOT_TRACK=true \
    ANONYMIZED_TELEMETRY=false

#### Other models #########################################################
## whisper TTS model settings ##
ENV WHISPER_MODEL="base" \
    WHISPER_MODEL_DIR="/app/backend/data/cache/whisper/models"

## RAG Embedding model settings ##
ENV RAG_EMBEDDING_MODEL="$USE_EMBEDDING_MODEL_DOCKER" \
    RAG_RERANKING_MODEL="$USE_RERANKING_MODEL_DOCKER" \
    SENTENCE_TRANSFORMERS_HOME="/app/backend/data/cache/embedding/models"

## Hugging Face download cache ##
ENV HF_HOME="/app/backend/data/cache/embedding/models"

## Torch Extensions ##
# ENV TORCH_EXTENSIONS_DIR="/.cache/torch_extensions"

#### Other models ##########################################################

WORKDIR /app/backend

ENV HOME /root
# Create user and group if not root
RUN if [ $UID -ne 0 ]; then \
    if [ $GID -ne 0 ]; then \
    addgroup --gid $GID app; \
    fi; \
    adduser --uid $UID --gid $GID --home $HOME --disabled-password --no-create-home app; \
    fi

RUN mkdir -p $HOME/.cache/chroma
RUN echo -n 00000000-0000-0000-0000-000000000000 > $HOME/.cache/chroma/telemetry_user_id

# Make sure the user has access to the app and root directory
RUN mkdir -p /app/backend/data
RUN chown -R $UID:$GID /app $HOME

RUN --mount=type=cache,mode=0777,target=/root/.cache/pip if [ "$USE_OLLAMA" = "true" ]; then \
    apt-get update && \
    # Install pandoc and netcat
    apt-get install -y --no-install-recommends git build-essential pandoc netcat-openbsd curl && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    # for RAG OCR
    apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 && \
    # install helper tools
    apt-get install -y --no-install-recommends curl jq && \
    # install ollama
    curl -fsSL https://ollama.com/install.sh | sh && \
    # cleanup
    rm -rf /var/lib/apt/lists/*; \
    else \
    apt-get update && \
    # Install pandoc, netcat and gcc
    apt-get install -y --no-install-recommends git build-essential pandoc gcc netcat-openbsd curl jq && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    # for RAG OCR
    apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 && \
    # cleanup
    rm -rf /var/lib/apt/lists/*; \
    fi

# install python dependencies
COPY --chown=$UID:$GID ./backend/requirements.txt ./requirements.txt

# RUN --mount=type=cache,mode=0777,target=/root/.cache/pip pip3 install uv

    # If you use CUDA the whisper and embedding model will be downloaded on first 
    # 去除了use--no-cache-dir 
RUN --mount=type=cache,mode=0777,target=/root/.cache/pip pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$USE_CUDA_DOCKER_VER
RUN --mount=type=cache,mode=0777,target=/root/.cache/pip pip3 install packaging ninja
    # 改为从本地安装
    # pip3 install flash-attn --no-build-isolation && \
    # 原来是用uv安装的
RUN --mount=type=cache,mode=0777,target=/root/.cache/pip pip3 install -r requirements.txt
RUN python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')"
RUN python -c "import os; from faster_whisper import WhisperModel; WhisperModel(os.environ['WHISPER_MODEL'], device='cpu', compute_type='int8', download_root=os.environ['WHISPER_MODEL_DIR'])";
RUN chown -R $UID:$GID /app/backend/data/

# 复制本地的whl文件到镜像中
COPY packages/flash_attn-2.6.2+cu123torch2.3cxx11abiTRUE-cp311-cp311-linux_x86_64.whl /app/

# 安装whl文件
RUN pip install /app/flash_attn-2.6.2+cu123torch2.3cxx11abiTRUE-cp311-cp311-linux_x86_64.whl

# copy embedding weight from build
# RUN mkdir -p /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2
# COPY --from=build /app/onnx /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx

# copy built frontend files
COPY --chown=$UID:$GID --from=build /app/build /app/build
COPY --chown=$UID:$GID --from=build /app/CHANGELOG.md /app/CHANGELOG.md
COPY --chown=$UID:$GID --from=build /app/package.json /app/package.json

# copy backend files
COPY --chown=$UID:$GID ./backend .

EXPOSE 8080

HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health | jq -ne 'input.status == true' || exit 1

USER $UID:$GID

ARG BUILD_HASH
ENV WEBUI_BUILD_VERSION=${BUILD_HASH}
ENV DOCKER true

CMD [ "bash", "start.sh"]
