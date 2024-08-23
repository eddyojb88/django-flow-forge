from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('trigger_pipeline_simple', views.trigger_pipeline_simple, name='trigger_pipeline_simple'),
    path('trigger_pipeline_simple_with_fail', views.trigger_pipeline_simple_with_fail, name='trigger_pipeline_simple_with_fail'),
    path('trigger_pipeline_ml_grid_search', views.trigger_pipeline_ml_grid_search, name='trigger_pipeline_ml_grid_search'),
    path('trigger_pipeline_simple_with_celery', views.trigger_pipeline_simple_with_celery, name='trigger_pipeline_simple_with_celery'),
    path('trigger_pipeline_parallel_with_celery', views.trigger_pipeline_parallel_with_celery, name='trigger_pipeline_parallel_with_celery'),
    path('fetch_custom_ml_viz_data/', views.fetch_custom_ml_viz_data, name='fetch_custom_ml_viz_data'),
    
]
