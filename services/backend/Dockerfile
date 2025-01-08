FROM python:3.12-slim-bookworm

# Assure UTF-8 encoding is used.
ENV LC_CTYPE=C.utf8

# Location of the virtual environment
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"

# Location of the python installation via uv
ENV UV_PYTHON_INSTALL_DIR="/python"

# Byte compile the python files on installation
ENV UV_COMPILE_BYTECODE=1

# Python verision to use
ENV UV_PYTHON=python3.12

# Tweaking the PATH variable for easier use
ENV PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH"

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates tzdata

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN uv venv /app/.venv

WORKDIR /app

# Create virtual environment and install dependencies
COPY ./app/pyproject.toml ./
COPY ./app/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . /app
