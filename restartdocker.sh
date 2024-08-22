#!/bin/bash

echo "Останавливаем контейнер"
docker stop lsbot
echo "Удаляем контейнер"
docker remove lsbot
echo "Билдим образ"
docker build -t konako/lsbot .
echo "Запускаем контейнер"
docker run --name=lsbot -d konako/lsbot
echo "Запущено"
