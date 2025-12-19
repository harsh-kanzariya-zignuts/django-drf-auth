# ===================================
# Stage 1: Builder
# ===================================
FROM python:3.12-slim AS builder

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/base.txt requirements/base.txt
COPY requirements/development.txt requirements/development.txt

# Install dependencies system-wide (no --user)
RUN pip install --upgrade pip && \
    pip install -r requirements/development.txt

# ===================================
# Stage 2: Runtime
# ===================================
FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder (system site-packages)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy bin scripts (gunicorn, etc.)
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app/

# Create non-root user
RUN useradd -m -u 1000 django && \
    chown -R django:django /app && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R django:django /app/staticfiles /app/media

# Switch to non-root user
USER django

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/admin/login/ || exit 1

# Default command
CMD ["gunicorn", "config.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "3", \
    "--timeout", "120", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info"]