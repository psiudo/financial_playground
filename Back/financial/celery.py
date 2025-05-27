# Back/financial/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financial.settings")
app = Celery("financial")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
