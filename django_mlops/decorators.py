from functools import wraps
import logging
from django.db import IntegrityError
from .models import ProcessTask
import types
import importlib


def define_task(process_name, depends_on=None):
    depends_on = depends_on or []
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Create or update the task in the database
        task, created = ProcessTask.objects.get_or_create(
            process_name=process_name, 
            task_name=func.__name__,
        )

        if created:
            # If the task is newly created, set dependencies
            logging.info('Process "%s" found task "%s". Registered in database' %(process_name, func.__name__))
            set_dependencies(task, depends_on, process_name)
        elif depends_on:
            # If updating and dependencies are provided, reset them
            task.dependencies.clear()
            set_dependencies(task, depends_on, process_name)

        return wrapper
    return decorator

def set_dependencies(task, depends_on, process_name):
    """
    Set dependencies for a task based on task names. Assumes that all dependent tasks
    belong to the same process as the task.

    :param task: The task instance to set dependencies for.
    :param depends_on: List of names of tasks that the task depends on.
    :param process_name: The name of the process the task belongs to.
    """
    for dep_name in depends_on:
        try:
            # Fetch the dependent task by name and process
            dependency = ProcessTask.objects.get(task_name=dep_name, process_name=process_name)
            task.dependencies.add(dependency)
        except ProcessTask.DoesNotExist:
            # Handle the case where a dependency does not exist
            logging.warning(f"Dependency task '{dep_name}' not found for process '{process_name}'.")
        except IntegrityError as e:
            logging.error(f"Error adding dependency: {e}")


def register_functions_from_module(module_obj):
    """
    Registers functions from a given module object to globals().

    Args:
        module_obj: The module object to import functions from.
    """
    for attribute_name in dir(module_obj):
        # Skip magic methods and attributes by checking for double underscores
        if attribute_name.startswith('__'):
            continue

        attribute = getattr(module_obj, attribute_name)
        # Check if the attribute is a callable and specifically a function (not classes, etc.)
        if callable(attribute) and isinstance(attribute, types.FunctionType):
            # Add the function to globals, making it callable globally
            globals()[attribute_name] = attribute
            print(f"Registered function: {attribute_name}")  # Optional: for confirmation