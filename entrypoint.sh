#!/usr/bin/env bash
set -e

# =============================================================================
#  entrypoint.sh — app (Django)
#  Fluxo: wait_for_db -> migrate (advisory lock) -> collectstatic --clear
#         -> runserver (dev) / gunicorn (prod)
# =============================================================================

echo "[entrypoint] Waiting for database..."
python manage.py wait_for_db --timeout 60

# ---------------------------------------------------------------------------
# Migrate with a PostgreSQL advisory lock so only one replica migrates at a
# time. Acquires a session-level lock, runs migrate and releases it. SQLite
# (used outside Docker) silently skips the lock step.
# ---------------------------------------------------------------------------
echo "[entrypoint] Running migrations (with advisory lock when available)..."
python <<'PYEOF'
import os
import subprocess
import sys

import django
from django.db import connection

django.setup()

lock_id = 0x53C51  # stable lock key shared across replicas
released = False
locked = False

try:
    vendor = connection.vendor
except Exception:
    vendor = None

if vendor == 'postgresql':
    with connection.cursor() as cursor:
        cursor.execute('SELECT pg_advisory_lock(%s)', [lock_id])
        locked = True
        print('[entrypoint] PostgreSQL advisory lock acquired.')
        try:
            subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
            cursor.execute('SELECT pg_advisory_unlock(%s)', [lock_id])
            released = True
        finally:
            if not released:
                cursor.execute('SELECT pg_advisory_unlock(%s)', [lock_id])
else:
    print('[entrypoint] Non-PostgreSQL backend; running migrate without advisory lock.')
    subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
PYEOF

echo "[entrypoint] Collecting static files (clear)..."
python manage.py collectstatic --clear --noinput

echo "[entrypoint] Starting application server..."
if [ "$1" = "gunicorn" ]; then
    exec "$@"
else
    exec python manage.py runserver 0.0.0.0:8000
fi