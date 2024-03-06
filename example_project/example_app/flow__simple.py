from django_flow_forge.flow_engine import register_task_flow

from datetime import datetime

def fetch_data1():    
    return 'Some data'

def fetch_data2():

    data1 = fetch_data_nested_1()
    data2 = fetch_data_nested_2()

    return f'{data1} & {data2}'

def fetch_data_nested_1():
    return 'nested_data1'

def fetch_data_nested_2():
    return 'nested_data2'

def clean_data():
    return True

# Analyzing data function
def analyze_data():
    # Simple analysis - just summarizing the data
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

# Training model function
def some_post_process_function():
    return 'Good Result!'

def register_pipelines():

    register_task_flow(
        flow_name='pipeline_simple',
        clear_existing_flow_in_db=True,
        pipeline = {
                    'fetch_data1': {'function': fetch_data1, 'depends_on': []},
                    'fetch_data2': {'function': fetch_data2, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1', 'fetch_data2']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'some_post_process_function': {'function': some_post_process_function, 'depends_on': ['analyze_data', 'clean_data']},
                    }

    )

    return

register_pipelines()