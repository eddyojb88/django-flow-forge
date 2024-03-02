import os
import django

# Initialize the Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

from example_project.example_app import flow__simple_with_celery
from example_project.example_app import flow___parallel_celery, flow__ml_grid_search
from django_flow_forge.tasks_db import run_flow


if __name__ == '__main__':

    kwargs = {
                'use_celery': True
                }
    # run_flow('trigger_pipeline_simple_with_celery', **kwargs)
    # run_flow('trigger_pipeline_in_parallel_with_celery', **kwargs)
    run_flow('pipeline_in_parallel_with_celery', **kwargs)
    