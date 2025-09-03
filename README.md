# photo-metadata-tool
## Overview

This is a basic tool to batch update the `Date Time Original` metadata based on a starting date/time, a timestep, and the file order.  It was implemented to easily update this information for scanned photos, which may not automatically have this metadata set.  Some cloud photo archives order photos by this metadata, and so adjusting the date/time for a whole batch of photos can be useful to maintain the order of scanning.

# Setup

## Docker

## Source

```bash
uv venv
uv pip install -e .
```

### [Deprecated] Original installation

```bash
uv init --name chronopix --package --python 3.11
uv add exif
```

# Usage

Scratchwork for deployment

```
docker run --rm -p 8501:8501 `
  -v "C:\Users\You\Pictures:/images:ro" `
  -e HOST_IMAGES_PATH="C:\Users\You\Pictures" `
  your/image
```