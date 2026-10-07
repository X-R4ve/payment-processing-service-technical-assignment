if [ -z "$(docker images -f 'reference=payment-processing-service' -q)" ]; then
  chmod +x ./build_image.sh
  ./build_image.sh
fi
docker compose -p payment-processing-service up -d