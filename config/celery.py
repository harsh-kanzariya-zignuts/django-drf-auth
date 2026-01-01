import os

from celery import Celery
from celery.signals import setup_logging

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# Create Celery app
app = Celery("config")

# Load config from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure Celery logging to use Django's logging config"""
    from logging.config import dictConfig

    from django.conf import settings
    
    dictConfig(settings.LOGGING)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery is working"""
    print(f"Request: {self.request!r}")