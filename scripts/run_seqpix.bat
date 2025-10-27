@echo off
setlocal

REM ==== CONFIG: update these for your project ====
set "PROJECT_DIR=C:\Users\mattp\photo-metadata-tool"
set "COMPOSE_FILE=docker-compose.yml"
set "COMPOSE_PROJECT_NAME=photo-metadata"
set "ENV_FILE=.env.windows"
set "APP_URL=http://localhost:8501"
REM ===============================================

REM Ensure Docker Desktop is running
docker info >NUL 2>&1
if errorlevel 1 (
  echo Starting Docker Desktop...
  start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  echo Waiting for Docker to be ready...
  :wait_docker
  timeout /t 2 /nobreak >NUL
  docker info >NUL 2>&1
  if errorlevel 1 goto wait_docker
)

REM Go to project
pushd "%PROJECT_DIR%" || (echo Failed to cd to %PROJECT_DIR% & exit /b 1)

REM Pull latest images (respects tags in your compose)
if defined ENV_FILE set "ENV_SWITCH=--env-file %ENV_FILE%"

echo Pulling latest images...
docker compose -p "%COMPOSE_PROJECT_NAME%" -f "%COMPOSE_FILE%" %ENV_SWITCH% pull
if errorlevel 1 (echo Pull failed & popd & exit /b 1)

echo Starting services...
docker compose -p "%COMPOSE_PROJECT_NAME%" -f "%COMPOSE_FILE%" %ENV_SWITCH% up -d --remove-orphans
if errorlevel 1 (echo Compose up failed & popd & exit /b 1)

popd

REM Open the app (optional)
if defined APP_URL start "" "%APP_URL%"

echo Done.
exit /b 0
