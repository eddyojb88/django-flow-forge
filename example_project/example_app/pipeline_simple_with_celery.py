from django_mlops.tasks_db import register_task_pipeline

from datetime import datetime

from celery import shared_task

@shared_task
def my_background_task(arg1, arg2):
    # Task implementation
    return arg1 + arg2

# Fetch data function
def fetch_data1():    
    result1 = my_background_task.delay(10, 100)
    result2 = my_background_task.delay(100, 1000)
    return (result1.get(), result2.get())

def clean_data():
    return True

# Analyzing data function
def analyze_data():
    # Simple analysis - just summarizing the data
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

# Training model function
def train_model():
    return 'Good Result!'

def register_pipelines():

    register_task_pipeline(
        process_name='trigger_pipeline_simple_with_celery',
        clear_existing_process_in_db=True,
        pipeline = {
                    'fetch_data1': {'function': fetch_data1, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1',]},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model, 'depends_on': ['analyze_data', 'clean_data']},
                    }

    )

    return

register_pipelines()