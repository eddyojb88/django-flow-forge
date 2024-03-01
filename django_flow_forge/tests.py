from django.test import TestCase
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from .models import Process, ProcessTask, ExecutedProcess, ExecutedTask
from .tasks_db import register_task, register_task_pipeline, resolve_dependencies_get_task_order, execute_task

class TaskRegistrationTests(TestCase):
    @patch('django_mlops.tasks_db.ProcessTask.objects.get_or_create')
    def test_register_task_creates_new_task(self, mock_get_or_create):
        mock_process = MagicMock()
        task_name = 'test_task'
        task_info = {'depends_on': [], 'depends_bidirectionally_with': []}
        nested = False
        mock_get_or_create.return_value = (mock_process, True)  # Simulates that the task was created

        register_task(mock_process, task_name, task_info, nested)

        mock_get_or_create.assert_called_once_with(
            task_name=task_name, 
            process=mock_process, 
            nested=nested,
        )

    # @patch('django_mlops.tasks_db.set_dependencies')
    # @patch('django_mlops.tasks_db.ProcessTask.objects.get_or_create')
    # def test_register_task_sets_dependencies(self, mock_get_or_create):
    #     mock_process = MagicMock()
    #     task_name = 'test_task_with_dependencies'
    #     task_info = {
    #         'depends_on': ['another_task'],
    #         'depends_bidirectionally_with': ['yet_another_task']
    #     }
    #     nested = False

    #     mock_task = MagicMock()
    #     mock_get_or_create.return_value = (mock_task, True)

    #     register_task(mock_process, task_name, task_info, nested)

# class PipelineRegistrationTests(TestCase):
#     @patch('django_mlops.tasks_db.Process.objects.get_or_create')
#     def test_register_task_pipeline_creates_process(self, mock_get_or_create):
#         process_name = 'test_process'
#         pipeline = [
#             {'task_name': 'task1', 'depends_on': [], 'nested_tasks': {}},
#             {'task_name': 'task2', 'depends_on': ['task1'], 'nested_tasks': {}}
#         ]
#         mock_process = MagicMock()
#         mock_get_or_create.return_value = (mock_process, True)  # Simulates that the task was created
#         register_task_pipeline(process_name, pipeline)

#         mock_get_or_create.assert_called_once_with(process_name=process_name)

# class TaskExecutionTests(TestCase):
#     @patch('django_mlops.tasks_db.execute_task')
#     @patch('django_mlops.tasks_db.Process.objects.get')
#     def test_execute_task_runs_successfully(self, mock_process_get, mock_execute_task):
#         mock_process_get.return_value = MagicMock()
#         task_name = 'executable_task'
#         process_name = 'executable_process'
#         mock_execute_task.return_value = True

#         # Assuming a simplified version of your run_process_pipeline function
#         success = execute_task({}, task_name, mock_process_get.return_value, MagicMock())

#         self.assertTrue(success)
#         mock_execute_task.assert_called_once()
