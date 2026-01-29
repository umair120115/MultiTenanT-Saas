# from celery import Celery
# import os




# # Set the default Django settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# app = Celery('core')

# # Load task modules from all registered Django app configs.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Auto-discover tasks in all installed apps (looks for tasks.py)
# app.autodiscover_tasks()
import os
from celery import Celery

# 1. Set the default Django settings module to 'core.settings'
# This matches your folder name "core"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. Rename the app to 'core' to match your project folder
app = Celery('core')

# 3. Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')