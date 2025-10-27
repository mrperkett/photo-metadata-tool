FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/mrperkett/photo-metadata-tool

# install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# install uv
RUN python3 -m pip install --no-cache-dir uv

# set directory into which source code will be copied
ENV APP_HOME=/photo-metadata-tool
WORKDIR ${APP_HOME}

# copy required files
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/
COPY app/ app/

# Create venv and install package with all dependencies
RUN uv sync --frozen

# Ensure venv is used by default
ENV PATH="${APP_HOME}/.venv/bin:${PATH}"

# default port is 8501, but this can be overridden by environment variable
ENV PORT 8501 
EXPOSE ${PORT}

# run the streamlit app
# CMD ["python", "-m", "streamlit", "run", "app/app.py", "--server.port=${PORT}"]
CMD bash -lc "uv run python3 -m streamlit run app/app.py --server.port=${PORT} --server.address=0.0.0.0"