FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl && \\
    curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock* ./

RUN uv venv /app/.venv && uv sync --no-dev
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

# The target commands vary based on compose service
CMD ["python", "main.py"]
