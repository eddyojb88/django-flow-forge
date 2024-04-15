from celery.result import AsyncResult
from celery import shared_task
from django.conf import settings
from .task_utils import TaskExecutor

class AsyncTaskExecutor:
    def submit_task(self, func, *args, **kwargs):
        """
        Submit a task for asynchronous execution.
        :param func: The function to execute.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: An identifier or a future object for the submitted task.
        """
        raise NotImplementedError

    def wait_for_results(self, task):
        """
        Wait for and retrieve the result of a task.
        :param task: The identifier or future object of the task.
        :return: The result of the task execution.
        """
        raise NotImplementedError
    

class CeleryTaskExecutor(TaskExecutor, AsyncTaskExecutor):

    def submit_task(self, **kwargs):
        """
        Executes the given task function, either with all provided keyword arguments or only those it accepts.

        Args:
            accepts_kwargs: A boolean indicating whether the function accepts arbitrary keyword arguments.
            func: The task function to be executed.
            **kwargs: Keyword arguments to be passed to the task function.

        Returns:
            The output of the task function.
        """

        self.task_run.status = 'in_progress'
        kwargs['current_task_name'] = self.task_name
        accepts_kwargs = self.function_accepts_kwargs(self.function)

        if accepts_kwargs:
            filtered_kwargs = kwargs
        
        else:
            filtered_kwargs = self.filter_kwargs_for_function(self.function, kwargs)
        
        if settings.DEBUG:
            self.debug_mode(**filtered_kwargs)
        else:
            self.task_future = self.function.delay(**filtered_kwargs)

        return
    
    def task_is_ready_for_close(self, **kwargs):
    
        if self.task_future.ready():
            return True
        
        return False

    def collect_and_store_output(self):

        self.task_output = self.task_future.get()
        self.executed_task_output()

        return

    def wait_for_results(self, task):
        assert isinstance(task, AsyncResult)
        return task.get()
