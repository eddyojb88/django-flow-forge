
from datetime import datetime
from celery import shared_task

from django_flow_forge.pipeline_engine import PipelineBase

class SimpleWithCeleryParallel(PipelineBase):

    def __init__(self):
        # Initialize instance attributes
        self.pipeline_name = 'celery_with_parallel_pipelines'
        self.pipeline = {
            self.fetch_data1: {},
            self.fetch_data2: {},
            self.analyze_data: {'depends_on': [self.fetch_data1, self.fetch_data2]},
        }
        # Call the base class's __init__ to register the pipeline
        super().__init__()
    
    @shared_task(bind=True)
    def fetch_data1(self, **kwargs):
        result = add_task(3,4)     
        return result
    
    @shared_task(bind=True)
    def fetch_data2(self, **kwargs):    
        result = add_task(10,4)     
        return result

    def analyze_data(self):
        analysis = f'Result of analysis.'
        return analysis

def add_task(arg1, arg2):
    # Task implementation
    return arg1 + arg2
