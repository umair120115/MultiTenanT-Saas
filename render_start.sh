#!/bin/bash

# Exit script on any error
set -e

echo "Applying Database Migrations..."
python manage.py migrate

echo "Collecting Static Files..."
python manage.py collectstatic --no-input

# Start Celery in the background (&)
# --concurrency=1 is CRITICAL for the Free Tier (512MB RAM) to prevent crashing
echo "Starting Celery Worker..."
celery -A core worker --loglevel=info --concurrency=1 &

# Start Gunicorn in the foreground
echo "Starting Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT