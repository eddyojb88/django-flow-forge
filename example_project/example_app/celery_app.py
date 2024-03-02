import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('example_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child flowes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
# app.autodiscover_tasks(['example_app',])

app.conf.update(
    broker_url='amqp://guest:guest@localhost',
    result_backend='rpc://',  # Using RabbitMQ with RPC backend
    # task_always_eager=True,  # Tasks will be executed locally instead of being sent to the queue.
)