from functools import wraps
import logging
from django.db import transaction
from django.utils import timezone
from .models import FlowTask, Flow, ExecutedFlow, ExecutedTask
from .task_utils import get_cytoscape_nodes_and_edges
from django.conf import settings
from django.utils import timezone
import time
import inspect

from django.db import transaction
from .models import Flow, FlowTask, BatchHandler, FlowBatch
from .task_utils import post_flow_graph_to_add_status, make_task_snapshot, make_flow_snapshot

flow_pipeline_lookup = {}

def register_task(flow, task_name, task_info, nested):
    """
    Registers or updates a single task within a specified flow, handling dependencies.

    This function is responsible for creating a new task or updating an existing one within the given flow. It also sets up dependencies between the task and others as specified in the `task_info` parameter.

    Parameters:
    - flow (Flow): The flow object to which the task belongs.
    - task_name (str): The name of the task to be registered or updated.
    - task_info (dict): A dictionary containing information about the task, including dependencies.
    - nested (bool): A flag indicating whether the task is nested within another task.

    Returns:
    - FlowTask: The created or updated task object.
    """
    # Extract dependency information from task_info
    depends_on = task_info.get('depends_on', [])
    depends_bidirectionally_with = task_info.get('depends_bidirectionally_with', [])
    
    function = task_info.get('function')
    
    # Create or update the task in the database
    task, _ = FlowTask.objects.get_or_create(
        task_name=task_name, 
        flow=flow,  # Associate with the specified flow
        nested=nested,
    )

    task.docstring = function.__doc__ if function else None
    task.code = inspect.getsource(function) if function else None

    # Set dependencies if any are specified
    if depends_on or depends_bidirectionally_with:
        set_dependencies(task, depends_on, depends_bidirectionally_with, flow)

    task.save()
    
    return task

def register_task_flow(flow_name, pipeline, clear_existing_flow_in_db=True, **kwargs):
    """
    Registers a pipeline of tasks for a specific flow, handling nested tasks and dependencies.

    This function sets up a complete pipeline of tasks for a given flow. It can also clear existing tasks and their relationships before setting up the new pipeline if required. The pipeline setup includes creating or updating tasks, setting dependencies, and ensuring that tasks no longer part of the pipeline are removed.

    Parameters:
    - flow_name (str): The name of the flow for which the pipeline is being registered.
    - pipeline (list of dict): A list of dictionaries, each representing a task and its details including dependencies and any nested tasks.
    - clear_existing_flow_in_db (bool, optional): Flag to clear existing tasks and relationships from the database for the given flow before registering the new pipeline. Defaults to True.

    Returns:
    - set: A set containing the names of the tasks that were updated or created as part of the pipeline.
    """
    # Create or retrieve the specified flow, and optionally clear existing tasks
    flow, created = Flow.objects.get_or_create(flow_name=flow_name)

    # Store the pipeline for reference
    global flow_pipeline_lookup
    flow_pipeline_lookup[flow_name] = pipeline
    
    if clear_existing_flow_in_db and not created:
        # If requested, delete all existing tasks for this flow to start fresh
        flow_tasks = FlowTask.objects.filter(flow=flow)
        flow_tasks.delete()
    
    with transaction.atomic():
        # Retrieve existing tasks for the flow to identify which ones to update or delete
        existing_tasks = set(FlowTask.objects.filter(flow=flow).values_list('task_name', flat=True))
        updated_tasks = set()

        def register_tasks_recursively(tasks, parent_flow, nested=False):
            """
            Recursively registers or updates tasks, including handling nested tasks.

            This internal function flowes each task in the provided task structure, registering them with the parent flow. It handles the creation or update of tasks, setting up their dependencies, and recursively flowes any nested tasks.

            Parameters:
            - tasks (dict): A dictionary of tasks to flow, where each key is a task name and each value is a task detail dictionary.
            - parent_flow (Flow): The flow object to which these tasks belong.
            - nested (bool): Indicates if the current tasks are nested within another task.
            """
            for task_name in tasks:
                # Register each task and add it to the set of updated tasks
                task = register_task(parent_flow, task_name, tasks[task_name], nested=nested)
                updated_tasks.add(task.task_name)

                # Flow any nested tasks
                nested_tasks = tasks[task_name].get('nested_tasks', [])
                if nested_tasks:
                    # Ensure nested tasks depend on their parent task if not already set
                    for j in nested_tasks:
                        nested_task = nested_tasks[j]
                        if task.task_name in nested_task['depends_bidirectionally_with']:
                            pass  # Dependency already exists
                        elif task.task_name not in nested_task['depends_on']:
                            nested_task['depends_on'].append(task.task_name)
                    register_tasks_recursively(nested_tasks, parent_flow, nested=True)

        # Start the pipeline flowing with the initial set of tasks
        register_tasks_recursively(pipeline, flow)

        # Identify and remove tasks that are no longer part of the pipeline
        tasks_to_delete = existing_tasks - updated_tasks
        if tasks_to_delete:
            FlowTask.objects.filter(flow=flow, task_name__in=tasks_to_delete).delete()

    return updated_tasks

def set_dependencies(task, depends_on, depends_bidirectionally_with, flow):
    """
    Sets dependencies for a given task within a flow. Dependencies can be unidirectional or bidirectional.
    
    This function links a task with its dependencies by creating or retrieving the dependent tasks and associating them
    accordingly. It ensures that each task is properly linked to others upon which it depends or with which it has
    bidirectional dependencies within the same flow.
    
    Parameters:
    - task (FlowTask): The task object for which dependencies are being set.
    - depends_on (list of str): A list of task names that the given task depends on. These are unidirectional dependencies.
    - depends_bidirectionally_with (list of str): A list of task names that have a bidirectional dependency with the given task.
    - flow (Flow): The flow instance to which these tasks belong.
    
    Returns:
    None
    """
    # print('here')
    for dep_name in depends_on:
        dep_task, _ = FlowTask.objects.get_or_create(
            task_name=dep_name, 
            flow=flow  # Link to the Flow instance
        )
        task.depends_on.add(dep_task)

    for dep_name in depends_bidirectionally_with:
        dep_task, _ = FlowTask.objects.get_or_create(
            task_name=dep_name, 
            flow=flow  # Link to the Flow instance
        )
        task.depends_bidirectionally_with.add(dep_task)
    
    return

def resolve_dependencies_get_task_order(flow_name):
    """
    Resolves task dependencies and determines the execution order for tasks within a given flow.
    
    This function identifies and resolves the dependencies among tasks in a flow to determine a valid execution order.
    It handles circular dependency detection and raises an exception if such a scenario is detected. The resolution
    flow ensures that all dependencies are accounted for before a task is marked as ready for execution.
    
    Parameters:
    - flow_name (str): The name of the flow for which tasks and their execution order are to be resolved.
    
    Returns:
    - all_task_objs (QuerySet): A QuerySet of all task objects associated with the given flow.
    - task_order (list of str): A list of task names in the order they should be executed, based on their dependencies.
    
    Raises:
    - Exception: If a circular dependency is detected among the tasks.
    """

    flow = Flow.objects.get(flow_name=flow_name)
    all_task_objs = FlowTask.objects.filter(flow=flow)
    dependency_map = {task.id: set(task.depends_on.values_list('id', flat=True)) for task in all_task_objs}
    resolved_tasks = []
    unresolved_tasks = []

    def resolve(task_id):
        if task_id in resolved_tasks:
            return
        if task_id in unresolved_tasks:
            raise Exception("Circular dependency detected")
        unresolved_tasks.append(task_id)

        for dependency in dependency_map.get(task_id, []):
            resolve(dependency)

        resolved_tasks.append(task_id)
        unresolved_tasks.remove(task_id)

    for task in all_task_objs:
        resolve(task.id)

    # Map resolved task IDs back to task names or objects as needed for execution
    task_order = [FlowTask.objects.get(id=task_id).task_name for task_id in resolved_tasks]
    return all_task_objs, task_order

def task_can_start_check(flow_run, task_name, executor, executors, **kwargs):

    try:
        if settings.DEBUG and kwargs.get('ignore_task_deps_in_debug_mode'):
            if (executor.task_run.status == 'pending') and any(executors[dep].task_run.status == 'failed' for dep in executor.depends_on):
                return False
            elif (executor.task_run.status == 'pending'):
                return True
        
        elif (executor.task_run.status == 'pending') and all(executors[dep].task_run.status == 'complete' for dep in executor.depends_on):
            return True

    except KeyError as ke:
        closing_flow_process(flow_run, flow_complete=False, status='failed')
        raise Exception(f'You may have a dependency issue in your flow for task {task_name}')
                
    return False

class DebugExecutor:
    '''
    An executor for the flow with the primary aim of assisting in debugging a flow, cycling through each
    Task function in an ordered and stepwise fashion
    '''
    def debug_mode(self, executor, **kwargs):
        executor.task_output = executor.function(**kwargs)
        return

def run_flow(flow_name, debug_executor=DebugExecutor(), flow_batch_id=None, **kwargs):
    '''
    Initiates and executes a flow pipeline by name, handling task execution and flow status updates.

    Parameters:
    - flow_name (str): The name of the xflow to be executed.
    - **kwargs: Additional keyword arguments that may be required for task execution.

    Notes:
    - It was decided not to use a TaskRun Object to store all details and methods of a Task Executor object - this may or may not have been an optimal decision
    '''

    try:
        # Attempt to fetch the flow definition and create a flow run instance
        flow = Flow.objects.get(flow_name=flow_name)
        flow_run = ExecutedFlow.objects.create(flow=flow, flow_id_snapshot=flow.id, flow_name_snapshot=flow.flow_name) 
        # Resolve task dependencies and determine the execution order
        all_task_objs, task_order = resolve_dependencies_get_task_order(flow_name)
        
    except Exception as e:
        logging.error(f"Failed to initiate flow run for {flow_name}: {e}")
        raise Exception('You may not have imported the pipeline in to the program, have spelt the flow wrong or are referring to a pipeline that no longer exists.')

    if flow_batch_id:
        batch = FlowBatch.objects.get(id=flow_batch_id)
        flow_run.flow_batch = batch
        if flow_name in batch.temp_data.get('executed_flows', []):
            print(f'''Not running flow "{flow_name}" Batch: f{batch.flow_batch_number} as it is flagged as already run''')
            return
        

    flow_pipeline = flow_pipeline_lookup.get(flow_name)
    flow_snapshot = make_flow_snapshot(flow_pipeline, task_order)
    flow_snapshot['graph'] = get_cytoscape_nodes_and_edges(all_task_objs, show_nested=True)
    flow_snapshot['flow_name'] = flow_name
    flow_run.flow_snapshot = flow_snapshot
    flow_run.failed_tasks = []
    if kwargs.get('flow_metadata'):
        flow_run.meta = kwargs.get('flow_metadata')
    flow_run.save()
    kwargs['executed_flow_id'] = flow_run.id
    kwargs['flow_name'] = flow_name
    kwargs['flow_batch_id'] = flow_batch_id
        
    executors = {}

    # assign an executor instance for each task:
    for task_name, task_dict in flow_pipeline.items():
        executor = get_executor(task_dict, task_name, **kwargs)
        executor.flow = flow
        executor.flow_run = flow_run
        executor.flow_name = flow_name
        executor.setup_flow_task(flow, flow_run,)
        executor.debug_executor = debug_executor
        executors[task_name] = executor


    '''Run the tasks using the list of executors'''
    counter = 0
    
    while any(executor.task_run.status != 'complete' for executor in executors.values()):

        for task_name in executors:

            executor = executors[task_name]

            ''' If all dependencies are met, execute the task. Else if all remaining tasks have dependencies that have failed, end flow '''
            if task_can_start_check(flow_run, task_name, executor, executors, **kwargs):

                executor.submit_task(**kwargs)

                executor.create_checkpoint()

                if executor.task_is_ready_for_close():
                    # collect output
                    executor.collect_and_store_output()

                    executor.task_post_process()
            
            # Additional Checks when in async mode
            elif executor.task_run.status == 'in_progress':
                
                # Else if task is in progress then check status and collect data #
                if counter % 1000 == 0:
                    executor.create_checkpoint()
        
                if executor.task_is_ready_for_close():
                    # collect output
                    executor.collect_and_store_output()

                    executor.task_post_process()

            elif executor.task_run.status == 'failed':
                flow_run.status = 'failed'
                post_flow_graph_to_add_status(flow_run)
                flow_run.save()
                break

        # Break the while loop if remaining tasks depend on tasks that have failed:
        flow_can_still_run = check_remaining_tasks_to_close_flow_run(flow_run, executors, **kwargs)
        if not flow_can_still_run:
            break
        
        # Optional: Implement a more sophisticated mechanism to avoid unnecessarily impatient looping
        time.sleep(1)
        counter += 1

    if all(executor.task_run.status == 'complete' for executor in executors.values()):
        closing_flow_process(flow_run, flow_complete=True, status='complete')
        logging.info(f"Flow {flow_name} completed successfully.")

    else:
        closing_flow_process(flow_run, flow_complete=False, status='incomplete')
        logging.error(f"Flow {flow_name} failed due to task error/s and dependency tree.")

    # Update the flow run status to 'complete' after successful execution of all tasks
    
    post_flow_graph_to_add_status(flow_run)
    flow_run.save()

    if flow_batch_id:
        batch = FlowBatch.objects.get(id=flow_batch_id)
        executed = batch.temp_data.get('executed_flows', [])
        executed.append(flow_name)
        batch.temp_data['executed_flows'] = executed
        batch.save(update_fields=['temp_data'])

    logging.info(f"Work Flow: {flow_name} ended.")

    return

def check_remaining_tasks_to_close_flow_run(flow_run, task_executors, **kwargs):

    flow_can_still_run = False
    # Get all remaining pending tasks

    # For each pending task, get the dependencies and check whether or can run or not
    for task_name in task_executors:
        executor = task_executors[task_name]
        failed_count = 0
        dependency_count = len(executor.depends_on)
        for dep in executor.depends_on:
            if (task_executors[dep].task_run.status == 'failed'):
                failed_count += 1
        
        # Set out conditions with which the flow can still run:
        if dependency_count == 0 and executor.task_run.status == 'pending':
            flow_can_still_run = True
        elif failed_count == 0 and executor.task_run.status == 'pending':
            flow_can_still_run = True

    return flow_can_still_run

def closing_flow_process(flow_run, flow_complete:bool, status=None,):

    flow_run.flow_complete = flow_complete
    flow_run.end_time = timezone.now()
    if status:
        flow_run.status = status
    flow_run.save()

    return

def is_celery_task(func):
    return hasattr(func, 'delay') and hasattr(func, 'apply_async')

def get_executor(task_dict, task_name, **kwargs):

    use_celery = kwargs.get('use_celery', False)
    if use_celery and is_celery_task(task_dict['function']):
        logging.info(f"Choosing Celery to execute task '{task_name}'.")
        from .async_utils import CeleryTaskExecutor
        executor = CeleryTaskExecutor(task_name, **task_dict)
    else:
        from .task_utils import TaskExecutor
        logging.debug(f"Using an in thread executor for {task_name}.")
        executor = TaskExecutor(task_name, **task_dict)
    return executor