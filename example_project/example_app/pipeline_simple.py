from django_mlops.tasks_db import register_task_pipeline

from datetime import datetime



''' Task definitions for 'data_science_project1' '''

# Fetch data function
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
def train_model():
    return 'Good Result!'

def clean_data():
    return

def analyze_data():
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

def train_model():
    print("Training model")

def register_pipelines():

    register_task_pipeline(
        process_name='pipeline_simple',
        clear_existing_process_in_db=True,
        pipeline = {
                    'fetch_data1': {'function': fetch_data1, 'depends_on': []},
                    'fetch_data2': {'function': fetch_data2, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1', 'fetch_data2']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model, 'depends_on': ['analyze_data', 'clean_data']},
                    }

    )

    return

register_pipelines()