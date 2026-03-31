FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock* README.md ./

RUN uv sync --frozen --no-install-project --no-dev
ENV PATH="/app/.venv/bin:$PATH"

COPY . .
ENV PYTHONPATH="/app/src"

# The target commands vary based on compose service
CMD ["python", "main.py"]
