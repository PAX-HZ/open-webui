#!/bin/bash

image_name="docker-image.paxengine.com.cn/ai-dev/sage:0.3.2"
container_name="sage"
host_port=3000
container_port=8080

# docker build -t "$image_name" . --build-arg="BUILDARG=true"
# docker stop "$container_name" &>/dev/null || true
# docker rm "$container_name" &>/dev/null || true

docker run -d --gpus=all \
    --volume=open-webui:/app/backend/data \
    --env=OLLAMA_BASE_URL=http://127.0.0.1:11444 \
    --workdir=/app/backend \
    --network=host \
    --name "$container_name" \
    --restart always \
    "$image_name" \
    bash start.sh

# docker image prune -f

docker run -d --gpus=all \
    --volume=open-webui:/app/backend/data \
    -e RAG_EMBEDDING_MODEL=intfloat/multilingual-e5-large \
    -e RAG_RERANKING_MODEL=intfloat/multilingual-e5-large \
    -e RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE=true -e RAG_RERANKING_MODEL_TRUST_REMOTE_CODE=true \
    -e HTTPS_PROXY=http://192.168.100.23:1081 -e HTTP_PROXY=http://192.168.100.23:1081 -e no_proxy=0.0.0.0,localhost,127.0.0.1 \
    --env=OLLAMA_BASE_URL=http://127.0.0.1:11444 \
    --workdir=/app/backend \
    --network=host \
    --name sage \
    --restart always \
    docker-image.paxengine.com.cn/ai-dev/sage:0.3.2 \
    bash start.sh