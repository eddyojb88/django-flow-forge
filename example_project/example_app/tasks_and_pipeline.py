from django_mlops.tasks_db import register_task_pipeline
from datetime import datetime


''' Task definitions for 'data_science_project1' '''

def fetch_data1():
    print("Fetching data 1")

def fetch_data_nested_1():
    return 'nested_data1'

def fetch_data_nested_2():
    return 'nested_data2'

def fetch_data2():
    print("Fetching data 2")
    data1 = fetch_service_data1()
    data2 = fetch_service_data2()
    return

def fetch_service_data1():
    service_data = call_api1()
    return service_data

def fetch_service_data2():
    return 'service_data1'

def call_api1():
    return 'api_call_data'

def clean_data():
    return True

def analyze_data():
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

def train_model():
    print("Training model")

def register_pipelines():

    register_task_pipeline(
        process_name='data_science_project_simple',
        clear_existing_process_in_db=True,
        pipeline = {
                    'fetch_data1': {'function': fetch_data1, 'depends_on': []},
                    'fetch_data2': {'function': fetch_data2, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1', 'fetch_data2']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model, 'depends_on': ['analyze_data', 'clean_data']},
                    }

    )

    register_task_pipeline(
        process_name='data_science_project_simple_v2', 
        clear_existing_process_in_db=True,
        pipeline = {
                    'fetch_data2': {'function': fetch_data2, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1', 'fetch_data2']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model, 'depends_on': ['analyze_data']},
                   }
    )


    ds_pipeline = {
                    'fetch_data': {'function': fetch_data1, 'depends_on': [], 
                                'nested_tasks': {
                                                    'fetch_data_nested_1': {
                                                        'function': fetch_data_nested_1,
                                                        'depends_on': [],
                                                        'depends_bidirectionally_with': ['fetch_data']
                                                    },
                                                    'fetch_data_nested_2': {
                                                        'function': fetch_data_nested_2,
                                                        'depends_on': ['fetch_data_nested_1'],
                                                        'depends_bidirectionally_with': ['fetch_data']
                                                    }
                                                }
                                    },
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model,'depends_on': ['analyze_data']}
            }

    register_task_pipeline(process_name='data_science_project_with_nesting', pipeline=ds_pipeline, clear_existing_process_in_db=True)

    return

register_pipelines()