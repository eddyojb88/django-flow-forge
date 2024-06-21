import inspect
import logging
from django.conf import settings
from django.utils import timezone
import sys
import traceback
from django.conf import settings

from .models import ExecutedTask, FlowTask

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
        self.flow_run.last_checkpoint_datetime = timezone.now()
        self.flow_run.save(update_fields=['last_checkpoint_datetime'])

    def submit_task(self, **kwargs):

        """
        Executes a specific task as part of a flow run, handling logging, execution, and status updates.

        """
        kwargs['current_task_name'] = self.task_name
        self.task_run.status = 'in_progress'
        accepts_kwargs = self.function_accepts_kwargs(self.function)

        if accepts_kwargs:
            filtered_kwargs = kwargs
            kwargs['flow_name'] = self.flow_name
            kwargs['task_name'] = self.task_name
            
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
        '''This is a dummy method in sync mode but used for async tasks'''
        return True

    def task_post_process(self):
        
        if getattr(settings, 'MLOPS_DEBUG', True):
            post_flow_graph_to_add_status(self.flow_run) # inefficient but potentially useful for debugging

        return
    
    def setup_flow_task(self, flow, flow_run, **kwargs):

        flow_task_obj = FlowTask.objects.get(task_name=self.task_name, flow=flow)
        
        # Check if the task has already been executed
        if ExecutedTask.objects.filter(flow_run=flow_run, task=flow_task_obj).exists():
            logging.info(f"Task {self.task_name} already executed.")
            return  # Task already executed

        logging.info(f"Setting up task: {self.task_name}...")

        self.task_snapshot = make_task_snapshot(flow_task_obj,)
        self.task_name_snapshot = self.task_name

        task_run = ExecutedTask.objects.create(
            flow_run=flow_run,
            task=flow_task_obj,
            task_snapshot_id=flow_task_obj.id,
            task_snapshot=self.task_snapshot,
            start_time=timezone.now(),
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
        if not FlowTask.objects.filter(id=self.task_run.task.id).exists():
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
        self.task_run.flow_run.failed_tasks.append(self.task_name)

        ''' If task no longer exists, remove it'''
        if not FlowTask.objects.filter(id=self.task_run.task.id).exists():
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

                    tasks_depends_bidirectionally_with = task.depends_bidirectionally_with.all()
                    if tasks_depends_bidirectionally_with.exists():
                        add_tasks_to_graph(tasks=tasks_depends_bidirectionally_with, target_task_id=task_id, 
                                        assigning_bidirectional_edges=True
                                        )

    # Start adding tasks to the graph; no parent_id for top-level tasks
    add_tasks_to_graph(tasks)

    # Prepare and return the graph data structured for Cytoscape
    graph_json = {
        'nodes': nodes,
        'edges': edges
    }

    return graph_json

def make_task_snapshot(flow_task_obj,):

    """
    Creates a snapshot of the given task's details.

    Args:
        flow_task_obj: An instance of FlowTask representing the task for which a snapshot is being created.

    Returns:
        A dictionary containing the snapshot of the task, including its ID, name, dependencies, bidirectional dependencies, and nested status.
    """

    task_snapshot = {
        'task_id': flow_task_obj.id,
        'task_name': flow_task_obj.task_name,
        # Assuming 'task' has the necessary information; adjust as necessary
        'depends_on': [dependency.task_name for dependency in flow_task_obj.depends_on.all()],
        'depends_bidirectionally_with': [dependency.task_name for dependency in flow_task_obj.depends_bidirectionally_with.all()],
        'nested': flow_task_obj.nested
    }

    return task_snapshot

def make_flow_snapshot(tasks_lookup, task_order):

    '''
    Creates a snapshot of the flow tasks based on the provided task order and lookup details.
    Each ExecutedFlow needs to store a snapshot of the tasks
    Each ExecutedTask might have an output which we need to explore data from from a click of the node on the graph viz
    Therefore, store the task run ids with the nodes too, otherwise, if the original task changes later on then there is no valid ref

    Parameters:
    - tasks_lookup (dict): A dictionary where keys are task names and values are dictionaries containing task details.
    - task_order (list): A list of task names representing the order in which tasks should be executed.

    Returns:
    - dict: A dictionary representing the snapshot of the flow, including tasks and their execution order.
 
    '''

    # Initialize the flow snapshot with task details
    flow_snapshot = {
        'tasks': [],
        'order': task_order
    }

    for task_name in task_order:
        task_details = tasks_lookup.get(task_name)
        if task_details:
            # Assume task_details includes necessary information; adjust as needed
            task_snapshot = {
                'name': task_name,
                'depends_on': task_details.get('depends_on', []),
            }
            flow_snapshot['tasks'].append(task_snapshot)
    
    return flow_snapshot

def post_flow_graph_to_add_status(flow_run):
    '''
    An inefficient add on in order to color nodes based on task status
    Updates the flow run snapshot with the execution status of each task for visualization purposes.

    Parameters:
    - flow_run (ExecutedFlow): The flow run instance to update.

    Returns:
    - ExecutedFlow: The updated flow run instance with task status information.
    '''

    # create index map:
    index_map = {}
    snapshot = flow_run.flow_snapshot
    nodes = snapshot['graph']['nodes']
    etasks = ExecutedTask.objects.filter(flow_run=flow_run,)
    for count, i in enumerate(nodes):
        index_map[i['data']['id']] = count
        etask = etasks.filter(task_snapshot_id=i['data']['id'])
        if len(etask) > 0:
            i['data']['status'] = etask[0].status
    snapshot['graph']['nodes'] = nodes
    flow_run.flow_snapshot = snapshot
    flow_run.save(update_fields=['flow_snapshot'])

    return