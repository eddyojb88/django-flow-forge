from celery import shared_task

from django_flow_forge.pipeline_engine import PipelineBase

class SimpleWithCelery(PipelineBase):

    def __init__(self):
        # Initialize instance attributes
        self.pipeline_name = 'pipeline_simple_with_celery'
        self.pipeline = {
            self.fetch_data1: {},
            self.fetch_data2: {},
            self.analyze_data: {'depends_on': [self.fetch_data1, self.fetch_data2]},
        }
        # Call the base class's __init__ to register the pipeline
        super().__init__()
    
    def fetch_data1(self):    
        result1 = my_background_task.delay(10, 100)
        result2 = my_background_task.delay(100, 1000)
        finished1 = result1.get()
        finished2 = result2.get()

        return (finished1, finished2)
    
    def fetch_data2(self):    
        result3 = my_background_task.delay(100, 10220)
        self.result = result3
        return (result3.get(),)
    
    def analyze_data(self):
        analysis = f'Result of analysis:  {self.result}'
        return analysis

    
@shared_task
def my_background_task(arg1, arg2):
    # Task implementation
    return arg1 + arg2