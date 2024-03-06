from django_flow_forge.flow_engine import register_task_flow

from datetime import datetime
from celery import shared_task


def add_task(arg1, arg2):
    # Task implementation
    return arg1 + arg2

@shared_task
def fetch_data1():    
    result = add_task(1,2)
    return result

@shared_task
def fetch_data2():   
    result = add_task(3,4)    
    return result

@shared_task
def clean_data():
    return True

@shared_task
def analyze_data():
    # Simple analysis - just summarizing the data
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

@shared_task
def post_process():
    return 'Good Result!'

def register_pipelines():

    register_task_flow(
        flow_name='pipeline_in_parallel_with_celery',
        clear_existing_flow_in_db=True,
        use_celery=True,
        pipeline = {
                    'fetch_data1': {'function': fetch_data1, 'depends_on': []},
                    'fetch_data2': {'function': fetch_data2, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1', 'fetch_data2']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'post_process': {'function': post_process, 'depends_on': ['analyze_data', 'clean_data']},
                    }

    )

    return

register_pipelines()