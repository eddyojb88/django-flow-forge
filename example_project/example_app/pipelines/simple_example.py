from django_flow_forge.pipeline_engine import PipelineBase
from datetime import datetime

class SimplePipeline(PipelineBase):

    def __init__(self):
        # Initialize instance attributes
        self.pipeline_name = 'pipeline_simple'
        self.pipeline = {
            self.fetch_data1: {'verbose_name': 'Fetch Data 1'},
            self.fetch_data2: {},
            self.clean_data: {'depends_on': [self.fetch_data1, self.fetch_data2],},
            self.analyze_data: {'depends_on': [self.clean_data]},
            self.some_post_process_function: {'depends_on': [self.analyze_data, self.clean_data], 'verbose_name':'Post Process'},
        }
        # Call the base class's __init__ to register the pipeline
        super().__init__()

    def fetch_data1(self):    
        """Fetches the first set of data."""
        self.dataset1 = 'some data'
        return

    def fetch_data2(self):
        """Fetches combined data from nested functions."""
        self.dataset2 = 'dataset 2'
        return 

    def clean_data(self):
        """Cleans the fetched data."""
        self.cleaned_data = self.dataset2
        return 'dataset cleaned'

    def analyze_data(self):
        """Analyzes the cleaned data and returns a summary."""
        analysis = 'Some Summary Analysis'
        return {'forecast_date': str(datetime.now()), 'analysis': analysis}

    def some_post_process_function(self):
        """Post-processes the analyzed data."""
        return