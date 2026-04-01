FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock* README.md ./
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
RUN uv sync --no-install-project --no-dev
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_LINK_MODE=copy

COPY . .
ENV PYTHONPATH="/app/src"

# The target commands vary based on compose service
CMD ["python", "main.py"]
