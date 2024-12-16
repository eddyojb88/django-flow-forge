from django.urls import path

from . import views

app_name = 'django-flow-forge'  # Set the namespace for this app's URLs

urlpatterns = [

    path('conceptual-dag-viz/', views.conceptual_dag_viz, name='conceptual-dag-viz'),
    path('update-conceptual-node-info/', views.update_conceptual_node_info, name='update-concept-node-info'),
    path('task-runs-viz/', views.tasks_run_viz, name='tasks_run_viz'),
    path('search-pipeline-runs/', views.search_pipeline_runs, name='search_pipeline_runs'),
    path('update-pipeline-graph/', views.update_pipeline_graph, name='update-pipeline-graph'),
    path('update-taskrun-node-info/', views.update_task_run_node_info, name='update-node-info'),
    path('update_pipeline_status/<int:pipeline_id>/update-status/', views.update_pipeline_status, name='update-pipeline-status'),
    
    path('display_ml_results/', views.display_ml_results_table, name='display_ml_results'),
    path('fetch_ml_viz_data/', views.fetch_ml_viz_data, name='fetch_ml_viz_data'),
    
]