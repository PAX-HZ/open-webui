image_name="docker-image.paxengine.com.cn/ai-dev/sage:V1.00.00_20241031"

docker build -t "$image_name" .
docker push "$image_name"