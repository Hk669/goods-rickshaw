# logistics_platform/celery.py

import os
import ssl
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistics_platform.settings')

app = Celery('logistics_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    broker_url=os.getenv('REDIS_URL'),
    result_backend=os.getenv('REDIS_URL'),
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED  # or CERT_OPTIONAL, CERT_NONE based on your needs
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED  # same as above
    }
)
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
