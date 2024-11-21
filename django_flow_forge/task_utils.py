import inspect
import logging
from django.conf import settings
from django.utils import timezone
import sys
import traceback
from django.conf import settings

from .models import ExecutedTask, PipelineTask

class TaskExecutor:

    def __init__(self, task_name, **task_dict):
        
        for key, value in task_dict.items():
            setattr(self, key, value)
        
        self.task_name = task_name
        self.task_output_ready = False
        self.task_future = None
        self.task_run = None
        self.task_output = None

    def create_checkpoint(self,):

        # If the task is async, you might want to handle the result differently                
        self.db_pipeline_run.last_checkpoint_datetime = timezone.now()
        self.db_pipeline_run.save(update_fields=['last_checkpoint_datetime'])

    def submit_task(self, **kwargs):

        """
        Executes a specific task as part of a flow run, handling logging, execution, and status updates.

        """
        kwargs['current_task_name'] = self.task_name
        self.task_run.status = 'in_progress'
        accepts_kwargs = self.function_accepts_kwargs(self.function)
        self.task_run.start_time=timezone.now()
        self.task_run.save(update_fields=['start_time'])


        if accepts_kwargs:
            filtered_kwargs = kwargs
            kwargs['pipeline_name'] = self.pipeline_name
            kwargs['task_name'] = self.task_name
            kwargs['executed_task_id'] = self.task_run.id
            
        else:
            filtered_kwargs = self.filter_kwargs_for_function(self.function, kwargs)

        if settings.DEBUG:
            
            try:
                self.debug_executor.debug_mode(self, **filtered_kwargs)
            
            finally:
                # Log any exception that occurred during task execution
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.info(f"exc_type: {exc_type}")
                if exc_type is not None:
                    traceback_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                    logging.error(f"An exception occurred during task execution:\n{traceback_str}")
                    # Pass the exception to failed_task_output
                    self.failed_task_output(traceback_str, **kwargs)
                    self.db_pipeline_run.status = 'failed'
                    self.parent_pipeline_obj.post_pipeline_graph_to_add_status()
                    self.db_pipeline_run.save()
        
        else:

            try:
                self.task_output = self.function(**filtered_kwargs)
                exc_type, exc_value, exc_traceback = sys.exc_info()
            
            except Exception as e:

                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.info(f"exc_type: {exc_type}")
                traceback_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logging.error(f"An exception occurred during task execution:\n{traceback_str}")
                # Pass the exception to failed_task_output
                self.failed_task_output(traceback_str, **kwargs)

        return

    def task_is_ready_for_close(self, **kwargs):
        '''This is a dummy method in sync mode, however in async tasks it is used'''
        return True

    def task_post_process(self):
        
        if getattr(settings, 'MLOPS_DEBUG', True):
            self.parent_pipeline_obj.post_pipeline_graph_to_add_status() # inefficient but potentially useful for debugging

        return
    
    def setup_pipeline_task(self, **kwargs):

        db_pipeline_task_obj = PipelineTask.objects.get(task_name=self.task_name, pipeline=self.db_pipeline)
        
        # Check if the task has already been executed
        if ExecutedTask.objects.filter(pipeline_run=self.db_pipeline_run, task=db_pipeline_task_obj).exists():
            logging.info(f"Task {self.task_name} already executed.")
            return  # Task already executed

        logging.info(f"Setting up task: {self.task_name}...")

        self.task_snapshot = make_task_snapshot(db_pipeline_task_obj,)
        self.task_name_snapshot = self.task_name

        task_run = ExecutedTask.objects.create(
            pipeline_run=self.db_pipeline_run,
            task=db_pipeline_task_obj,
            task_snapshot_id=db_pipeline_task_obj.id,
            task_snapshot=self.task_snapshot,
            # start_time=timezone.now(),
        )
        
        self.task_run = task_run

        return

    def executed_task_output(self,):

        logging.info(f"Task {self.task_name} has finished execution.")
        if self.task_run.status == 'failed':
            pass
        
        else:
            self.task_run.output = self.task_output
            self.task_run.task_complete = True
            self.task_run.end_time = timezone.now()
            self.task_run.status = 'complete'

        ''' If task no longer exists, remove it'''

        if self.task_run.task and not PipelineTask.objects.filter(id=self.task_run.task.id).exists():
            self.task_run.task = None

        self.task_run.save(update_fields=['status', 'end_time', 'task_complete', 'output'])

        return True

    def collect_and_store_output(self):

        '''Collection is only necessary for async tasks that override this method'''

        self.executed_task_output()

        return

    def failed_task_output(self, e, **kwargs):
        logging.info(f"Failed Task: {self.task_name}.")
        self.task_run.status = 'failed'
        self.task_run.end_time = timezone.now()
        self.task_run.exceptions['main_run'] = str(e)
        self.task_run.output = str(e)
        self.task_run.pipeline_run.failed_tasks.append(self.task_name)

        ''' If task no longer exists, remove it'''
        if not PipelineTask.objects.filter(id=self.task_run.task.id).exists():
            self.task_run.task = None
            
        self.task_run.save(update_fields=['status', 'end_time', 'exceptions',])
        return False
    
    def function_accepts_kwargs(self, func):
        """
        Check if the function accepts **kwargs.
        """
        sig = inspect.signature(func)
        return any(param.kind == param.VAR_KEYWORD for param in sig.parameters.values())

    def filter_kwargs_for_function(self, func, kwargs):
        """
        Filter kwargs to only include keys that match the function's parameters.
        If the function accepts **kwargs, return the original kwargs.
        """
        if self.function_accepts_kwargs(func):
            return kwargs  # Return original kwargs if **kwargs is accepted

        sig = inspect.signature(func)
        func_params = sig.parameters
        filtered_kwargs = {key: value for key, value in kwargs.items() if key in func_params}

        return filtered_kwargs
    
def get_cytoscape_nodes_and_edges(tasks, show_nested=False):
    
    nodes = []
    edges = []

    def add_tasks_to_graph(tasks, target_task_id=None, assigning_bidirectional_edges=False):

        for task in tasks:

            if not show_nested and task.nested:
                pass

            else:
                # Ensure each task has a unique identifier; using task.id for uniqueness
                task_id = str(task.id)  # Convert to string to ensure compatibility with Cytoscape
                task_node = {'data': {'id': task_id, 'label': task.task_name}}
                if task_node not in nodes:
                    nodes.append(task_node)

                # If the task has a parent, add an edge indicating the dependency direction
                if target_task_id:
                    # nested_js_bool = str(task.nested).lower()  # Used to segregate nested nodes:
                    # if task.nested:
                        # print('here')
                    edge = {'data': {'source': task_id, 'target': target_task_id, 'nested': task.nested}}
                    if edge not in edges:
                        edges.append(edge)

                if not assigning_bidirectional_edges:
                    # Recursively add nested tasks' dependencies
                    parent_tasks = task.depends_on.all()
                    if parent_tasks.exists():
                        add_tasks_to_graph(tasks=parent_tasks, target_task_id=task_id)

    # Start adding tasks to the graph; no parent_id for top-level tasks
    add_tasks_to_graph(tasks)

    # Prepare and return the graph data structured for Cytoscape
    graph_json = {
        'nodes': nodes,
        'edges': edges
    }

    return graph_json

def make_task_snapshot(db_pipeline_task_obj,):

    """
    Creates a snapshot of the given task's details.

    Args:
        pipeline_task_obj: An instance of PipelineTask representing the task for which a snapshot is being created.

    Returns:
        A dictionary containing the snapshot of the task, including its ID, name, dependencies, bidirectional dependencies, and nested status.
    """

    task_snapshot = {
        'task_id': db_pipeline_task_obj.id,
        'task_name': db_pipeline_task_obj.task_name,
        # Assuming 'task' has the necessary information; adjust as necessary
        'depends_on': [dependency.task_name for dependency in db_pipeline_task_obj.depends_on.all()],
    }

    return task_snapshot