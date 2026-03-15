import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bergline.settings.development_sqlite")

app = Celery("bergline")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
