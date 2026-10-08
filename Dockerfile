FROM python:3.11-slim

WORKDIR /app

# Copy dependency configuration and source files
COPY pyproject.toml ./
COPY src ./src

# Install package and dependencies, create non-root user
RUN pip install --no-cache-dir . && useradd -m appuser

USER appuser

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "querypilot.server"]
