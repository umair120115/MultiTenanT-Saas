#!/bin/bash

# 1. Run migrations safely
python manage.py migrate

# 2. Start the Celery worker in the background (the '&' is critical)
celery -A core worker --loglevel=info &

# 3. Start Gunicorn (the web server) in the foreground
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT