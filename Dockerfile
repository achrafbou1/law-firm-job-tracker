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

# Run the application
CMD ["uv", "run", "python", "main.py"]
