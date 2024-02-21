from functools import wraps
import logging
from django.db import transaction, IntegrityError
import json
from django.utils import timezone
from .models import ProcessTask, Process, ExecutedProcess, ExecutedTask
from .task_utils import get_cytoscape_nodes_and_edges

from django.db import transaction
from .models import Process, ProcessTask

process_pipeline_lookup = {}

def set_dependencies(task, depends_on, depends_bidirectionally_with, process):
    """
    Helper function to set task dependencies based on their names and process.
    """
    # print('here')
    for dep_name in depends_on:
        dep_task, _ = ProcessTask.objects.get_or_create(
            task_name=dep_name, 
            process=process  # Link to the Process instance
        )
        task.depends_on.add(dep_task)

    for dep_name in depends_bidirectionally_with:
        dep_task, _ = ProcessTask.objects.get_or_create(
            task_name=dep_name, 
            process=process  # Link to the Process instance
        )
        task.depends_bidirectionally_with.add(dep_task)
    
    return

def register_task(process, task_name, task_info, nested):
    """
    Helper function to create or update a task and its dependencies for a given process.
    """
    depends_on = task_info.get('depends_on', [])
    depends_bidirectionally_with = task_info.get('depends_bidirectionally_with', [])
    
    task, _ = ProcessTask.objects.get_or_create(
        task_name=task_name, 
        process=process,  # Associate with the specified process
        nested=nested,
    )

    if depends_on or depends_bidirectionally_with:
        set_dependencies(task, depends_on, depends_bidirectionally_with, process)

    return task

def register_task_pipeline(process_name, pipeline, clear_existing_process_in_db=False):
    """
    Registers a pipeline of tasks for a given process, including nested tasks,
    creating or updating tasks as necessary, setting dependencies, cleaning up
    tasks not part of the updated pipeline, and optionally clearing any existing tasks and relationships.

    :param process_name: The name of the process the tasks belong to.
    :param pipeline: A list of dictionaries, each representing a task and its details.
    :param clear_existing_process_in_db: Boolean indicating whether to clear existing tasks and relationships.
    """

    process, created = Process.objects.get_or_create(process_name=process_name)

    global process_pipeline_lookup
    process_pipeline_lookup[process_name] = pipeline
    
    if clear_existing_process_in_db and not created:
        # Delete all tasks associated with this process to clear existing relationships
        ProcessTask.objects.filter(process=process).delete()
    
    with transaction.atomic():
        existing_tasks = set(ProcessTask.objects.filter(process=process).values_list('task_name', flat=True))
        updated_tasks = set()

        def register_tasks_recursively(tasks, parent_process, nested=False):
            """
            Recursively processes and registers tasks, including any nested tasks.
            """
            for task_name in tasks:
                task = register_task(parent_process, task_name, tasks[task_name], nested=nested)
                updated_tasks.add(task.task_name)

                # Check for and process any nested tasks
                nested_tasks = tasks[task_name].get('nested_tasks', [])
                if nested_tasks:
                    # ensure nested tasks depend on parent_process
                    for j in nested_tasks:
                        nested_task = nested_tasks[j]
                        if task.task_name in nested_task['depends_bidirectionally_with']:
                            pass

                        elif task.task_name not in nested_task['depends_on']:

                            nested_task['depends_on'].append(task.task_name)

                    register_tasks_recursively(nested_tasks, parent_process, nested=True)

        # Start processing the pipeline with potential nested tasks
        register_tasks_recursively(pipeline, process)

        # Remove tasks not part of the updated pipeline
        tasks_to_delete = existing_tasks - updated_tasks
        if tasks_to_delete:
            ProcessTask.objects.filter(process=process, task_name__in=tasks_to_delete).delete()

        return updated_tasks

def fetch_process_pipeline(process_name):
    return process_pipeline_lookup.get(process_name)

def resolve_dependencies_get_task_order(process_name):

    process = Process.objects.get(process_name=process_name)
    all_task_objs = ProcessTask.objects.filter(process=process)
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
    task_order = [ProcessTask.objects.get(id=task_id).task_name for task_id in resolved_tasks]
    return all_task_objs, task_order

def make_process_snapshot(tasks_lookup, task_order):

    '''
    Each ExecutedProcess needs to store a snapshot of the tasks
    Each ExecutedTask might have an output which we need to explore data from from a click of the node on the graph viz
    Therefore, store the task run ids with the nodes too, otherwise, if the original task changes later on then there is no valid ref
    '''

    # Initialize the process snapshot with task details
    process_snapshot = {
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
            process_snapshot['tasks'].append(task_snapshot)
    
    return process_snapshot

def run_process_pipeline(process_name):

    try:
        process = Process.objects.get(process_name=process_name)
        process_run = ExecutedProcess.objects.create(process=process, process_id_snapshot=process.id, process_name_snapshot=process.process_name) 
        all_task_objs, task_order = resolve_dependencies_get_task_order(process_name)
        
    except Exception as e:
        logging.error(f"Failed to initiate process run for {process_name}: {e}")
        return

    process_pipeline = fetch_process_pipeline(process_name)
    process_snapshot = make_process_snapshot(process_pipeline, task_order)
    process_snapshot['graph'] = get_cytoscape_nodes_and_edges(all_task_objs, show_nested=True)
    process_snapshot['process_name'] = process_name
    process_run.process_snapshot = process_snapshot
    process_run.save()

    logging.info(f"Starting task execution for process '{process_name}'.")

    for task_name in task_order:
        task_dict = process_pipeline[task_name]

        execute_task(task_dict, task_name, process, process_run,)

    process_run.end_time = timezone.now()
    process_run.process_complete = True
    process_run.save()

    logging.info(f"All tasks for process {process_name} completed successfully.")

def make_task_snapshot(process_task_obj,):

    task_snapshot = {
        'task_id': process_task_obj.id,
        'task_name': process_task_obj.task_name,
        # Assuming 'task' has the necessary information; adjust as necessary
        'depends_on': [dependency.task_name for dependency in process_task_obj.depends_on.all()],
        'depends_bidirectionally_with': [dependency.task_name for dependency in process_task_obj.depends_bidirectionally_with.all()],
        'nested': process_task_obj.nested
    }

    return task_snapshot

def execute_task(task_dict, task_name, process, process_run,):

    process_task_obj = ProcessTask.objects.get(task_name=task_name, process=process)
    
    # Check if the task has already been executed
    if ExecutedTask.objects.filter(process_run=process_run, task=process_task_obj).exists():
        logging.info(f"Task {task_name} already executed.")
        return  # Task already executed

    logging.info(f"Executing task: {task_name}...")

    task_snapshot = make_task_snapshot(process_task_obj,)

    task_run = ExecutedTask.objects.create(
        process_run=process_run,
        task=process_task_obj,
        task_snapshot_id=process_task_obj.id,
        task_snapshot=task_snapshot,
        start_time=timezone.now(),
    )

    task_output = task_dict['function']()  # Execute the task

    task_run.output=task_output
    task_run.task_complete = True
    task_run.end_time = timezone.now()
    task_run.save()

    logging.info(f"Task {task_name} executed successfully.")

    return



