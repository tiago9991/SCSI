FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# System dependencies required by PostgreSQL client libs, Pillow, ReportLab
# and curl (used by container healthchecks).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Entrypoints and scripts
COPY entrypoint.sh /app/entrypoint.sh
COPY entrypoint.celery.sh /app/entrypoint.celery.sh
RUN chmod +x /app/entrypoint.sh /app/entrypoint.celery.sh

# Default command is overridden by docker-compose per service
CMD ["/app/entrypoint.sh"]