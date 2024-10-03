
from functools import wraps
import logging
from django.db import transaction
from django.utils import timezone
from .models import PipelineTask, Pipeline, ExecutedPipeline, ExecutedTask, BatchHandler, PipelineBatch
from django.conf import settings
import time
import inspect
from django.db import transaction

from .models import Pipeline, PipelineTask

pipeline_lookup = {}
# global pipeline_lookup
class DebugExecutor:
    '''
    An executor for the pipeline with the primary aim of assisting in debugging a pipeline, cycling through each
    Task function in an ordered and stepwise fashion
    '''
    def debug_mode(self, executor, **kwargs):
        if hasattr(executor.function, 'apply_async'):
            executor.task_future = executor.function.delay(**kwargs)
        else:
            executor.task_output = executor.function(**kwargs)

        return


class PipelineBase:

    def __init__(self):
        # Base class initialization logic
        self.register_pipeline()
        pass
    
    def register_pipeline(self):
        """Registers the task pipeline pipeline."""
        self.register_pipeline_tasks()
        self.create_pipeline_dict_by_names()
        return

    def create_pipeline_dict_by_names(self):
        # Create the alternate lookup dictionary
        self.pipeline_by_names = {}
        for task_function, task_info in self.pipeline.items():
            task_name = task_function.__name__
            
            # Extract the function names for the dependencies
            depends_on_functions = task_info.get('depends_on', [])
            depends_on_names = [dep.__name__ for dep in depends_on_functions]
            
            # Create the dictionary entry with the function and other task info
            self.pipeline_by_names[task_name] = {
                'function': task_function,
                'depends_on': depends_on_functions,  # Keep the original functions
                'depends_on_task_names': depends_on_names,  # Add the function names as a separate entry
                **task_info  # Include other task information like 'verbose_name', etc.
            }

        return

    @staticmethod
    def delete_all_existing_pipelines():
        print('Deleting all pipelines')
        Pipeline.objects.all().delete()
        print('Deleting all Tasks')
        PipelineTask.objects.all().delete()


    def register_pipeline_tasks(self, clear_existing_pipeline_in_db=True):
        """
        Registers a pipeline of tasks for a specific pipeline, handling dependencies.
        """
        # Create or retrieve the specified pipeline, and optionally clear existing tasks
        db_pipeline, created = Pipeline.objects.get_or_create(pipeline_name=self.pipeline_name)
        self.db_pipeline = db_pipeline
        self.db_pipeline_id = db_pipeline.id

        if clear_existing_pipeline_in_db and not created:
            # If requested, delete all existing tasks for this pipeline to start fresh
            PipelineTask.objects.filter(pipeline=db_pipeline).delete()

        with transaction.atomic():
            # Register each task in the pipeline
            updated_tasks = set()
            for task, task_info in self.pipeline.items():
                db_task_obj = self.register_task(db_pipeline, task, task_info,)
                updated_tasks.add(db_task_obj.task_name)

            # Remove tasks that are no longer in the pipeline
            existing_tasks = set(PipelineTask.objects.filter(pipeline=db_pipeline).values_list('task_name', flat=True))
            tasks_to_delete = existing_tasks - updated_tasks
            if tasks_to_delete:
                PipelineTask.objects.filter(pipeline=self.db_pipeline, task_name__in=tasks_to_delete).delete()

        global pipeline_lookup
        pipeline_lookup[self.pipeline_name] = self

        db_pipeline.save()

        return

    def register_task(self, db_pipeline, task, task_info):
        """
        Registers or updates a single task within a specified pipeline, handling dependencies.
        """
        # Extract dependency information from task_info
        depends_on = task_info.get('depends_on', [])
        task_function = task
        verbose_task_name = task_info.get('verbose_name')
        task_name = task.__name__

        # Create or update the task in the database
        db_task, _ = PipelineTask.objects.get_or_create(task_name=task_name, pipeline=db_pipeline,)
        if verbose_task_name:
            db_task.verbose_name = verbose_task_name
        db_task.docstring = task_function.__doc__ if task_function else None
        db_task.code = inspect.getsource(task_function) if task_function else None

        # Set dependencies if any are specified
        self.set_dependencies(db_task, depends_on, db_pipeline)

        db_task.save()

        return db_task

    def set_dependencies(self, db_task, depends_on, db_pipeline):
        """
        Sets dependencies for a given task within a pipeline.
        """
        for task_function in depends_on:
            dep_name = task_function.__name__
            dep_task, _ = PipelineTask.objects.get_or_create(task_name=dep_name, pipeline=db_pipeline)
            db_task.depends_on.add(dep_task)

        return
    
    def run(self, debug_executor=DebugExecutor(), pipeline_batch_id=None, **kwargs):
        '''

        '''
            
        try:
            # Attempt to fetch the pipeline definition and create a pipeline run instance
            db_pipeline_run = ExecutedPipeline(pipeline=self.db_pipeline, 
                                            pipeline_id_snapshot=self.db_pipeline.id, 
                                            pipeline_name_snapshot=self.pipeline_name)

            if pipeline_batch_id:
                batch = PipelineBatch.objects.get(id=pipeline_batch_id)
                db_pipeline_run.pipeline_batch = batch
                if self.pipeline_name in batch.temp_data.get('executed_pipelines', []):
                    print(f'''Not running pipeline "{self.pipeline_name}" Batch: f{batch.pipeline_batch_number} as it is flagged as already run''')
                    return

            db_pipeline_run.save()
            self.db_pipeline_run = db_pipeline_run
            # Resolve task dependencies and determine the execution order
            all_db_task_objs, task_order = self.resolve_dependencies_get_task_order()
            self.all_db_task_objs = all_db_task_objs
            self.task_order = task_order
            # Reorder self.pipeline_by_names based on self.task_order
            self.pipeline_by_names = {task_name: self.pipeline_by_names[task_name] for task_name in self.task_order}
            
        except Exception as e:
            logging.error(f"Failed to initiate pipeline run for {self.pipeline_name}: {e}")
            raise Exception('You may not have imported the pipeline in to the program, have spelt the pipeline wrong or are referring to a pipeline that no longer exists.')

        pipeline_snapshot = self.make_pipeline_snapshot()
        pipeline_snapshot['graph'] = self.get_cytoscape_nodes_and_edges()
        pipeline_snapshot['pipeline_name'] = self.pipeline_name
        db_pipeline_run.pipeline_snapshot = pipeline_snapshot
        db_pipeline_run.failed_tasks = []
        if kwargs.get('pipeline_metadata'):
            db_pipeline_run.meta = kwargs.get('pipeline_metadata')
        db_pipeline_run.save()
        kwargs['executed_pipeline_id'] = db_pipeline_run.id
        kwargs['pipeline_name'] = self.pipeline_name
        kwargs['pipeline_batch_id'] = pipeline_batch_id
            
        self.task_executors = {}

        # assign an executor instance for each task:
        for task_name in self.pipeline_by_names:
            executor = self.get_executor(task_name, **kwargs)
            executor.pipeline = self.pipeline
            executor.db_pipeline = self.db_pipeline
            executor.db_pipeline_run = db_pipeline_run
            executor.pipeline_name = self.pipeline_name
            executor.setup_pipeline_task()
            executor.parent_pipeline_obj = self
            executor.debug_executor = debug_executor
            self.task_executors[task_name] = executor


        '''Run the tasks using the list of self.task_executors'''
        counter = 0
        
        while any(executor.task_run.status != 'complete' for executor in self.task_executors.values()):

            pipeline_can_still_run = True

            for task_name in self.task_executors:

                executor = self.task_executors[task_name]

                ''' If all dependencies are met, execute the task. Else if all remaining tasks have dependencies that have failed, end pipeline '''
                if self.task_can_start_check(executor, **kwargs):

                    executor.submit_task(**kwargs)

                    executor.create_checkpoint()

                # Additional Checks when in async mode
                elif executor.task_run.status == 'in_progress':
                    
                    # Else if task is in progress then check status and collect data #
                    if counter % 1000 == 0:
                        executor.create_checkpoint()
            
                elif executor.task_run.status == 'failed':
                    self.db_pipeline_run.status = 'failed'
                    self.post_pipeline_graph_to_add_status()
                    self.db_pipeline_run.save()
                    pipeline_can_still_run = self.check_remaining_tasks_to_close_pipeline_run(**kwargs)
                    if not pipeline_can_still_run:
                        break

                if pipeline_can_still_run and executor.task_run.status != 'failed' and executor.task_is_ready_for_close():
                    # collect output
                    executor.collect_and_store_output()

                    executor.task_post_process()
                
            if not pipeline_can_still_run:
                break
            
            # Optional: Implement a more sophisticated mechanism to avoid unnecessarily impatient looping
            time.sleep(1)
            counter += 1

        if all(executor.task_run.status == 'complete' for executor in self.task_executors.values()):
            self.closing_pipeline_process(pipeline_complete=True, status='complete')
            logging.info(f"Pipeline {self.pipeline_name} completed successfully.")

        else:
            self.closing_pipeline_process(pipeline_complete=False, status='incomplete')
            logging.error(f"Pipeline {self.pipeline_name} failed due to task error/s and dependency tree.")

        # Update the pipeline run status to 'complete' after successful execution of all tasks
        
        self.post_pipeline_graph_to_add_status()
        self.db_pipeline_run.save()

        # Only set a batch as executed if its complete
        if pipeline_batch_id and (all(executor.task_run.status == 'complete' for executor in self.task_executors.values())):
            batch = PipelineBatch.objects.get(id=pipeline_batch_id)
            executed = batch.temp_data.get('executed_pipelines', [])
            executed.append(self.pipeline_name)
            batch.temp_data['executed_pipelines'] = executed
            batch.save(update_fields=['temp_data'])

        logging.info(f"Pipeline Flow: {self.pipeline_name} ended.")

        return
    
    def task_can_start_check(self, executor, **kwargs):

        try:
            ''' If we dont care about fulfilling task depencies in debug mode then go ahead and run '''
            if settings.DEBUG and kwargs.get('ignore_task_deps_in_debug_mode'):
                if (executor.task_run.status == 'pending') and any(self.task_executors[dep].task_run.status == 'failed' for dep in executor.depends_on_task_names if dep in self.task_executors):
                    return False
                elif (executor.task_run.status == 'pending'):
                    return True
            
            elif (executor.task_run.status == 'pending') and all(self.task_executors[dep].task_run.status == 'complete' for dep in executor.depends_on_task_names):
                return True

            elif (executor.task_run.status == 'pending') and any(self.task_executors[dep].task_run.status == 'failed' for dep in executor.depends_on_task_names):
                executor.task_run.status = 'failed'
                return False
        except KeyError as ke:
            self.closing_pipeline_process(pipeline_complete=False, status='failed')
            raise Exception(f'You may have a dependency issue in your pipeline for task {executor.task_name}')
                    
        return False

    def check_remaining_tasks_to_close_pipeline_run(self, **kwargs):
        '''Recursively check dependency tree to see if any other tasks should run'''

        def count_failed_dependencies(task_name):
            """Recursively count failed dependencies for a given task."""
            executor = self.task_executors[task_name]
            failed_count = 0
            
            for dep in executor.depends_on_task_names:
                # If the dependency has failed, increment the failed count
                if self.task_executors[dep].task_run.status == 'failed':
                    failed_count += 1
                # Recursively check the dependencies of the dependency
                failed_count += count_failed_dependencies(dep)
            
            return failed_count

        pipeline_can_still_run = False
        
        # Check all tasks in the pipeline
        for task_name in self.task_executors:
            executor = self.task_executors[task_name]
            
            if executor.task_run.status == 'pending':
                failed_count = count_failed_dependencies(task_name)
                dependency_count = len(executor.depends_on)
                
                # Set conditions under which the pipeline can still run:
                if dependency_count == 0 and executor.task_run.status == 'pending':
                    pipeline_can_still_run = True
                elif failed_count == 0 and executor.task_run.status == 'pending':
                    pipeline_can_still_run = True

        return pipeline_can_still_run

    def closing_pipeline_process(self, pipeline_complete:bool, status=None,):

        self.db_pipeline_run.pipeline_complete = pipeline_complete
        self.db_pipeline_run.end_time = timezone.now()
        if status:
            self.db_pipeline_run.status = status
        self.db_pipeline_run.save()

        return

    @staticmethod
    def is_celery_task(func):
        return hasattr(func, 'delay') and hasattr(func, 'apply_async')

    def get_executor(self, task_name, **kwargs):

        use_celery = kwargs.get('use_celery', False)
        if use_celery and self.is_celery_task(self.pipeline_by_names[task_name]['function']):
            logging.info(f"Choosing Celery to execute task '{task_name}'.")
            from .async_utils import CeleryTaskExecutor
            executor = CeleryTaskExecutor(task_name, **self.pipeline_by_names[task_name])
        else:
            from .task_utils import TaskExecutor
            logging.debug(f"Using an in thread executor for {task_name}.")
            executor = TaskExecutor(task_name, **self.pipeline_by_names[task_name])
        return executor
    
    def resolve_dependencies_get_task_order(self):
        """
        Resolves task dependencies and determines the execution order for tasks within a given pipeline.
        
        """

        all_task_objs = PipelineTask.objects.filter(pipeline=self.db_pipeline)
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
        task_order = [PipelineTask.objects.get(id=task_id).task_name for task_id in resolved_tasks]
        return all_task_objs, task_order
    
    def make_pipeline_snapshot(self,):

        '''
        Creates a snapshot of the pipeline tasks based on the provided task order and lookup details.
        Each ExecutedPipeline needs to store a snapshot of the tasks
        Each ExecutedTask might have an output which we need to explore data from from a click of the node on the graph viz
        Therefore, store the task run ids with the nodes too, otherwise, if the original task changes later on then there is no valid ref

        Parameters:
        - tasks_lookup (dict): A dictionary where keys are task names and values are dictionaries containing task details.
        - task_order (list): A list of task names representing the order in which tasks should be executed.

        Returns:
        - dict: A dictionary representing the snapshot of the pipeline, including tasks and their execution order.
    
        '''

        # Initialize the pipeline snapshot with task details
        pipeline_snapshot = {'tasks': [], 'order': self.task_order}

        for task_name in self.task_order:
            task_details = self.pipeline_by_names[task_name]
            if task_details:
                # Assume task_details includes necessary information; adjust as needed
                task_snapshot = {'name': task_name, 'depends_on': task_details.get('depends_on_task_names', []),}
                pipeline_snapshot['tasks'].append(task_snapshot)
        
        return pipeline_snapshot
    
    def get_cytoscape_nodes_and_edges(self,):
        
        nodes = []
        edges = []

        def add_tasks_to_graph(tasks, target_task_id=None,):

            for task in tasks:

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

                # Recursively add nested tasks' dependencies
                parent_tasks = task.depends_on.all()
                if parent_tasks.exists():
                    add_tasks_to_graph(tasks=parent_tasks, target_task_id=task_id)


        # Start adding tasks to the graph; no parent_id for top-level tasks
        add_tasks_to_graph(self.all_db_task_objs)

        # Prepare and return the graph data structured for Cytoscape
        graph_json = {
            'nodes': nodes,
            'edges': edges
        }

        return graph_json
        
    def post_pipeline_graph_to_add_status(self,):
        '''
        An inefficient add on in order to color nodes based on task status
        Updates the pipeline run snapshot with the execution status of each task for visualization purposes.

        Parameters:
        - pipeline_run (ExecutedPipeline): The pipeline run instance to update.

        Returns:
        - ExecutedPipeline: The updated pipeline run instance with task status information.
        '''

        # create index map:
        index_map = {}
        snapshot = self.db_pipeline_run.pipeline_snapshot
        nodes = snapshot['graph']['nodes']
        etasks = ExecutedTask.objects.filter(pipeline_run=self.db_pipeline_run,)
        for count, i in enumerate(nodes):
            index_map[i['data']['id']] = count
            etask = etasks.filter(task_snapshot_id=i['data']['id'])
            if len(etask) > 0:
                i['data']['status'] = etask[0].status
        snapshot['graph']['nodes'] = nodes
        self.db_pipeline_run.pipeline_snapshot = snapshot
        self.db_pipeline_run.save(update_fields=['pipeline_snapshot'])

        return

