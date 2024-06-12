#!/bin/bash

# host_port=11444
# container_port=11434

# # read -r -p "Do you want ollama in Docker with GPU support? (y/n): " use_gpu

# docker rm -f ollama || true
# # docker pull ollama/ollama:latest
# # docker run -d --gpus=all -e HTTPS_PROXY=http://192.168.100.23:1081 -e HTTP_PROXY=http://192.168.100.23:1081 -e no_proxy=0.0.0.0,localhost,127.0.0.1 -v ~/models:/models -v ~/ollama:/ollama -v /usr/share/ollama/.ollama:/root/.ollama -p 11444:11434 --name ollama docker-image.paxengine.com.cn/ai-dev/ollama:0.1.43
# docker_args="-d -v ollama:/root/.ollama -p $host_port:$container_port --name ollama ollama/ollama"

# # if [ "$use_gpu" = "y" ]; then
# docker_args="--gpus=all $docker_args"
# # fi

# docker run $docker_args

# docker image prune -f
docker run -d --gpus=all -e HTTPS_PROXY=http://192.168.100.23:1081 -e HTTP_PROXY=http://192.168.100.23:1081 -e no_proxy=0.0.0.0,localhost,127.0.0.1 -v ~/models:/models -v ~/ollama:/ollama -v /usr/share/ollama/.ollama:/root/.ollama -p 11444:11434 --name ollama docker-image.paxengine.com.cn/ai-dev/ollama:0.1.43