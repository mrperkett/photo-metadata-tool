# photo-metadata-tool
## Overview

This is a basic tool to batch update the `Date Time Original` metadata based on a starting date/time, a timestep, and the file order.  It was implemented to easily update this information for scanned photos, which may not automatically have this metadata set.  Some cloud photo archives order photos by this metadata, and so adjusting the date/time for a whole batch of photos can be useful to maintain the order of scanning.

# Setup

## Docker

```bash
docker build -t photo-metadata-tool .
```

## Source

```bash
git clone git@github.com:mrperkett/photo-metadata-tool.git

cd photo-metadata-tool

. .venv/bin/activate

uv sync
#uv pip install -e .


```

### [Deprecated] Original installation

```bash
uv init --name chronopix --package --python 3.11
uv add exif
uv add --dev tomli
uv lock
```

# Development

```bash
docker login ghcr.io -u mrperkett # NOTE: password is the PAT
make build
make push
```

# Deploy

Deploying to Windows


Right-click the .bat → Create shortcut → drag to Desktop.

Optional: In shortcut Properties → Run, choose Minimized.



# Usage

## Docker

```bash
# Running on Linux accepting client-provided Windows paths
docker compose --env-file .env.linux_run_with_nt_user_paths up

docker compose --env-file .env.linux_run_with_linux_user_paths up

docker compose --env-file .env.nt_run_with_nt_user_paths up
```

For reference, here are the equivalent docker run commands.

Alternatively, if you don't want to use `docker-compose`, you can run the following.

```bash
PORT=8501
USER_OS="nt"
USER_MOUNT_PATH="/home/mperkett"
INTERNAL_MOUNT_PATH="/data"
docker run -it --rm \
    -e port=${PORT} \
    -e USER_OS="${USER_OS}" \
    -e USER_MOUNT_PATH="${USER_MOUNT_PATH}" \
    -e INTERNAL_MOUNT_PATH="${INTERNAL_MOUNT_PATH}"
    -p ${PORT}:${PORT} \
    -v "${USER_MOUNT_PATH}":"${INTERNAL_MOUNT_PATH}" \
    photo-metadata-tool
```

### Linux deployment

Running on a Linux machine.

```bash
docker compose --env-file .env.linux up
```


## Source




### Run in WSL accepting a POSIX path as user input


### Run in WSL accepting a Windows path as user input

```bash
PORT=8501
USER_OS="nt"
USER_MOUNT_PATH="C:/Users/mattp"
INTERNAL_MOUNT_PATH="/data"
uv run python -m streamlit run --server.port=8501 app/app.py
```


### Run in Windows accepting a POSIX path as user input


### Run in Windows accepting a Windows path as user input
