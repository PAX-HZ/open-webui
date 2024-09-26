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
# cpu only
docker run -d --gpus=all \
    --volume=open-webui:/app/backend/data \
    -e RAG_EMBEDDING_MODEL=BAAI/bge-m3 \
    -e RAG_RERANKING_MODEL=BAAI/bge-m3 \
    -e RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE=true -e RAG_RERANKING_MODEL_TRUST_REMOTE_CODE=true \
    -e HTTPS_PROXY=http://192.168.100.23:1081 -e HTTP_PROXY=http://192.168.100.23:1081 -e no_proxy=0.0.0.0,localhost,127.0.0.1,192.168.*.* \
    -e USE_CUDA_DOCKER=false \
    --env=OLLAMA_BASE_URL=http://127.0.0.1:11444 \
    --workdir=/app/backend \
    --network=host \
    --name sage \
    --restart always \
    docker-image.paxengine.com.cn/ai-dev/sage:0.3.2 \
    bash start.sh

# sage-hz
docker run -d --gpus=all \
    --volume=open-webui:/app/backend/data \
    -v /opt/nltk_data:/opt/nltk_data \
    -e RAG_EMBEDDING_MODEL=BAAI/bge-m3 \
    -e RAG_RERANKING_MODEL=BAAI/bge-m3 \
    -e RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE=true -e RAG_RERANKING_MODEL_TRUST_REMOTE_CODE=true \
    -e HTTPS_PROXY=http://192.168.100.23:1081 -e HTTP_PROXY=http://192.168.100.23:1081 -e no_proxy=0.0.0.0,localhost,127.0.0.1,192.168.*.* \
    -e NLTK_DATA=/opt/nltk_data \
    -e USE_CUDA_DOCKER=true \
    --env=OLLAMA_BASE_URL=http://127.0.0.1:11444 \
    --workdir=/app/backend \
    --network=host \
    --name sage \
    --restart always \
    docker-image.paxengine.com.cn/ai-dev/sage:0.3.7 \
    bash start.sh

# sage-us
docker run -d --gpus=all \
    --volume=open-webui-us:/app/backend/data \
    -v /opt/nltk_data:/opt/nltk_data \
    -e RAG_EMBEDDING_MODEL=BAAI/bge-m3 \
    -e RAG_RERANKING_MODEL=BAAI/bge-m3 \
    -e RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE=true -e RAG_RERANKING_MODEL_TRUST_REMOTE_CODE=true \
    -e NLTK_DATA=/opt/nltk_data \
    -e USE_CUDA_DOCKER=true \
    --env=OLLAMA_BASE_URL=http://host.docker.internal:11444 \
    --workdir=/app/backend \
    -p 8083:8080 \
    --add-host=host.docker.internal:host-gateway \
    --name sage-us \
    docker-image.paxengine.com.cn/ai-dev/sage:0.3.12 \
    bash start.sh

# test for new version
docker run -it --gpus=all \
    --volume=open-webui:/app/backend/data \
    -v /opt/nltk_data:/opt/nltk_data \
    -e RAG_EMBEDDING_MODEL=BAAI/bge-m3 \
    -e RAG_RERANKING_MODEL=BAAI/bge-m3 \
    -e RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE=true -e RAG_RERANKING_MODEL_TRUST_REMOTE_CODE=true \
    -e HTTPS_PROXY=http://192.168.100.23:1081 -e HTTP_PROXY=http://192.168.100.23:1081 -e no_proxy=0.0.0.0,localhost,127.0.0.1,192.168.*.* \
    -e NLTK_DATA=/opt/nltk_data \
    -e USE_CUDA_DOCKER=true \
    --env=OLLAMA_BASE_URL=http://127.0.0.1:11444 \
    --workdir=/app/backend \
    -p 8082:8080 \
    --name sage-test \
    docker-image.paxengine.com.cn/ai-dev/sage:0.3.7 \
    bash start.sh