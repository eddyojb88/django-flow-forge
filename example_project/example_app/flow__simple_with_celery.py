from django_flow_forge.flow_engine import register_task_flow

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

def fetch_data2():    
    result3 = my_background_task.delay(100, 10220)
    return (result3.get(),)

def clean_data():
    return True

# Analyzing data function
def analyze_data():
    # Simple analysis - just summarizing the data
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

# Training model function
def post_process():
    return 'Good Result!'

def register_pipelines():

    register_task_flow(
        flow_name='trigger_pipeline_simple_with_celery',
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