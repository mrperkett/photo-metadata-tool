@echo off
set "PROJECT_DIR=C:\Users\mattp\code\photo-metadata-tool"
set "COMPOSE_FILE=docker-compose.yml"
set "COMPOSE_PROJECT_NAME=photo-metadata"
pushd "%PROJECT_DIR%" && docker compose -p "%COMPOSE_PROJECT_NAME%" -f "%COMPOSE_FILE%" down && popd
