from django.urls import path
from . import views

urlpatterns = [

    path('conceptual-dag-viz/', views.conceptual_dag_viz, name='conceptual-dag-viz'),
    path('task-runs-viz/', views.tasks_run_viz, name='tasks_run_viz'),
    path('update-node-info/', views.update_node_info, name='update-node-info'),
    path('display_ml_results/', views.display_ml_results_table, name='display_ml_results'),
    path('fetch_ml_viz_data/', views.fetch_ml_viz_data, name='fetch_ml_viz_data'),
]