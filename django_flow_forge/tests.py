# from django.test import TestCase
# from django.db import IntegrityError
# from unittest.mock import patch, MagicMock
# from .models import Process, ProcessTask, ExecutedProcess, ExecutedTask
# # from .flow_engine import register_task, register_task_pipeline, resolve_dependencies_get_task_order, execute_task

# class TaskRegistrationTests(TestCase):
#     @patch('django_flow_forge.tasks_db.ProcessTask.objects.get_or_create')
#     def test_register_task_creates_new_task(self, mock_get_or_create):
#         mock_flow = MagicMock()
#         task_name = 'test_task'
#         task_info = {'depends_on': [], 'depends_bidirectionally_with': []}
#         nested = False
#         mock_get_or_create.return_value = (mock_flow, True)  # Simulates that the task was created

#         register_task(mock_flow, task_name, task_info, nested)

#         mock_get_or_create.assert_called_once_with(
#             task_name=task_name, 
#             flow=mock_flow, 
#             nested=nested,
#         )

#     # @patch('django_flow_forge.tasks_db.set_dependencies')
#     # @patch('django_flow_forge.tasks_db.ProcessTask.objects.get_or_create')
#     # def test_register_task_sets_dependencies(self, mock_get_or_create):
#     #     mock_flow = MagicMock()
#     #     task_name = 'test_task_with_dependencies'
#     #     task_info = {
#     #         'depends_on': ['another_task'],
#     #         'depends_bidirectionally_with': ['yet_another_task']
#     #     }
#     #     nested = False

#     #     mock_task = MagicMock()
#     #     mock_get_or_create.return_value = (mock_task, True)

#     #     register_task(mock_flow, task_name, task_info, nested)

# # class PipelineRegistrationTests(TestCase):
# #     @patch('django_flow_forge.tasks_db.Process.objects.get_or_create')
# #     def test_register_task_pipeline_creates_flow(self, mock_get_or_create):
# #         flow_name = 'test_flow'
# #         pipeline = [
# #             {'task_name': 'task1', 'depends_on': [], 'nested_tasks': {}},
# #             {'task_name': 'task2', 'depends_on': ['task1'], 'nested_tasks': {}}
# #         ]
# #         mock_flow = MagicMock()
# #         mock_get_or_create.return_value = (mock_flow, True)  # Simulates that the task was created
# #         register_task_pipeline(flow_name, pipeline)

# #         mock_get_or_create.assert_called_once_with(flow_name=flow_name)

# # class TaskExecutionTests(TestCase):
# #     @patch('django_flow_forge.tasks_db.execute_task')
# #     @patch('django_flow_forge.tasks_db.Process.objects.get')
# #     def test_execute_task_runs_successfully(self, mock_flow_get, mock_execute_task):
# #         mock_flow_get.return_value = MagicMock()
# #         task_name = 'executable_task'
# #         flow_name = 'executable_flow'
# #         mock_execute_task.return_value = True

# #         # Assuming a simplified version of your run_flow_pipeline function
# #         success = execute_task({}, task_name, mock_flow_get.return_value, MagicMock())

# #         self.assertTrue(success)
# #         mock_execute_task.assert_called_once()
