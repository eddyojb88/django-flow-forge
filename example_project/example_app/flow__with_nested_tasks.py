from django_flow_forge.flow_engine import register_task_flow

from datetime import datetime


def fetch_data1():
    return

def fetch_data2():

    data1 = nested_data_task1()
    data2 = nested_data_task2()

    return

def nested_data_task1():
    return

def nested_data_task2():
    return

def clean_data():
    # Load some data, clean it then store it
    return

def analyze_data():
    # Load data, analyse it then store and return an output
    return {'forecast_date': str(datetime.now()), 'analysis': 'Some Summary Analysis'}

def post_process_function(**kwargs):    
    return 'A great result!'

def register_pipelines():

    ds_pipeline = {
                    'fetch_data': {'function': fetch_data1, 'depends_on': [], 
                                'nested_tasks': {
                                                    'fetch_metadata': {
                                                        'function': nested_data_task1,
                                                        'depends_on': [],
                                                        'depends_bidirectionally_with': ['fetch_data'],
                                                    },
                                                    'fetch_tiktok_data': {
                                                        'function': nested_data_task2,
                                                        'depends_on': ['fetch_metadata'],
                                                        'depends_bidirectionally_with': ['fetch_data']
                                                    }
                                                }
                                    },
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'post_process_function': {'function': post_process_function,'depends_on': ['analyze_data']}
            }

    register_task_flow(flow_name='pipeline_with_nested_tasks', pipeline=ds_pipeline, clear_existing_flow_in_db=True)

    return

register_pipelines()