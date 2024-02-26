from django.apps import AppConfig

from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.db import connection


class ExampleAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'example_app'

    # def ready(self):


@receiver(connection_created)
def set_sqlite_pragma(sender, connection=None, **kwargs):
    if connection.vendor == 'sqlite':
        print('Amending sqlite to handle concurrent tasks')
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.close()
