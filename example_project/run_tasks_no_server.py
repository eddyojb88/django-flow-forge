import os
import django

# Initialize the Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

from example_app.pipelines.simple_example import SimplePipeline
from example_app.pipelines.simple_example_with_failure import SimplePipelineFail
from example_app.pipelines.ml_grid_search_example import MLGridSearchPipeline
from example_app.pipelines.simple_example_with_celery import SimpleWithCelery
from example_app.pipelines.celery_with_parallel_pipelines import SimpleWithCeleryParallel

from example_app.celery_app import app  # Make sure this matches the path to your Celery app

from django_flow_forge.auto_register_pipelines import auto_register_pipelines

# Call the function to find and instantiate pipelines
auto_register_pipelines()

if __name__ == '__main__':

    kwargs = {}

    pipeline = SimplePipeline()
    pipeline.run()

    # pipeline = SimplePipelineFail(**kwargs)
    # pipeline.run()

    # MLGridSearchPipeline().run()

    # SimpleWithCeleryParallel().run(use_celery=True)
    
    # SimpleWithCelery().run(use_celery=True)

    





    
    