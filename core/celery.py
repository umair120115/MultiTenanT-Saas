from celery import Celery
import os




# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas.settings')

app = Celery('saas')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps (looks for tasks.py)
app.autodiscover_tasks()