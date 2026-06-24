#!/usr/bin/env bash
set -e

# =============================================================================
#  entrypoint.celery.sh — celery_worker / celery_beat
#  Fluxo: wait_for_db apenas. Nunca roda migrations nem collectstatic.
# =============================================================================

echo "[entrypoint.celery] Waiting for database..."
python manage.py wait_for_db --timeout 60

echo "[entrypoint.celery] Starting: $@"
exec "$@"