FROM python:3.13-slim

WORKDIR /app

# Add app to PYTHONPATH
ENV PYTHONPATH=/app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

RUN ls .venv/bin

# Run the application
CMD [".venv/bin/python", "main.py"]
