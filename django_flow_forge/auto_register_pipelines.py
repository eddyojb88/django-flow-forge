import os
import importlib.util
import inspect
import sys
from django.conf import settings

# Use BASE_DIR from Django settings
BASE_DIR = settings.BASE_DIR

# Name of the base class to look for
BASE_CLASS_NAME = 'PipelineBase'

def should_register_pipelines(to_ignore):
    """Check if the current command should register pipelines or not."""
    return not any(command in sys.argv for command in to_ignore)

def find_pipeline_directories(base_dir):
    """Recursively finds all directories named 'pipelines' in the project."""
    pipeline_dirs = []
    for root, dirs, files in os.walk(base_dir):
        if 'pipelines' in dirs:
            pipeline_dirs.append(os.path.join(root, 'pipelines'))
    return pipeline_dirs

def find_pipeline_classes(pipeline_dir):
    """Finds and returns all classes that inherit from PipelineBase in a given directory."""
    pipeline_classes = []
    for file_name in os.listdir(pipeline_dir):
        if file_name.endswith('.py'):
            file_path = os.path.join(pipeline_dir, file_name)
            module_name = f"{os.path.basename(pipeline_dir)}.{file_name[:-3]}"

            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Iterate through all members of the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if the class inherits from PipelineBase and is not PipelineBase itself
                    if BASE_CLASS_NAME in [base.__name__ for base in obj.__bases__]:
                        pipeline_classes.append(obj)
    return pipeline_classes

def instantiate_and_register_pipelines(pipeline_classes):
    """Instantiates each pipeline class and explicitly calls register_pipeline."""

    ''' Delete all existing pipelines and tasks'''
    pipeline_class = pipeline_classes[0]
    pipeline_class.delete_all_existing_pipelines()

    for pipeline_class in pipeline_classes:
        # try:
        instance = pipeline_class()  # Instantiate the pipeline class
        # instance.register_pipeline()  # Explicitly register the pipeline
        print(f"Successfully instantiated and registered: {pipeline_class.__name__}")
        # except Exception as e:
            # print(f"Failed to instantiate or register {pipeline_class.__name__}: {str(e)}")

def auto_register_pipelines(to_ignore=None):
    # Default commands to ignore
    default_to_ignore = ['makemigrations', 'migrate', 'loaddata', 'dumpdata', 'compress']
    
    # Use the provided to_ignore list, or default if None is provided
    to_ignore = to_ignore if to_ignore is not None else default_to_ignore

    # Check if pipelines should be registered based on command-line arguments
    if should_register_pipelines(to_ignore):
        # Find all pipeline directories
        pipeline_dirs = find_pipeline_directories(BASE_DIR)

        # For each directory, find and instantiate pipeline classes
        for pipeline_dir in pipeline_dirs:
            print(f"Searching in directory: {pipeline_dir}")
            pipeline_classes = find_pipeline_classes(pipeline_dir)
            instantiate_and_register_pipelines(pipeline_classes)
    else:
        print("Skipping pipeline registration due to command in to_ignore list.")
