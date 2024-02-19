from django.urls import path
from . import views

urlpatterns = [

    path('conceptual-dag-viz/', views.conceptual_dag_viz, name='conceptual-dag-viz'),
    path('task-runs-viz/', views.tasks_run_viz, name='tasks_run_viz'),
    # path('dag-viz-component/', views.dag_viz_view, name='dag-viz-component'),
]