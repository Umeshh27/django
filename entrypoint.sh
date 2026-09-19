#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be available..."

while ! python -c "
import socket
import os
host = os.environ.get('POSTGRES_HOST', 'db')
port = int(os.environ.get('POSTGRES_PORT', 5432))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
try:
    s.connect((host, port))
    s.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping 1s"
    sleep 1
done

echo "PostgreSQL is ready!"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Seeding initial project, issue, and comment data..."
python manage.py seed_db

echo "Collecting static assets..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
