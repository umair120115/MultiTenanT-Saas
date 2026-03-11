#!/bin/bash

# 1. Prepare static files
python manage.py collectstatic --noinput

# 2. Run database migrations (keeps your Supabase schema up to date)
python manage.py migrate

# 3. Start the Celery worker in the background
# The '&' at the end is what allows the script to keep moving
celery -A core worker --loglevel=info &

# 4. Start Gunicorn + Uvicorn in the foreground
# 'exec' ensures this process handles system signals properly for graceful shutdowns
exec gunicorn core.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000