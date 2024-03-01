from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from django_flow_forge.tasks_db import run_flow_pipeline
from django_flow_forge import models as mlops_models

 # This is important in order to load up your tasks and allow django_ml_ops to register each task
from . import pipeline_simple, pipeline_with_nested_tasks, pipeline_simple_ml, pipeline_ml_grid_search
from . import  pipeline_simple_with_celery

def index(request):
    return render(request, 'example_app/index.html')

def trigger_pipeline_simple(request):
    run_flow_pipeline('pipeline_simple')
    return HttpResponse("'Pipeline Simple' Executed", status=200)

def trigger_pipeline_with_nested_tasks(request):
    run_flow_pipeline('pipeline_with_nested_tasks')
    return HttpResponse("'pipeline_with_nested_tasks' executed", status=200)

def trigger_pipeline_simple_ml(request):
    run_flow_pipeline('pipeline_simple_ml')
    return HttpResponse("'pipeline_simple_ml' executed", status=200)

def trigger_pipeline_ml_grid_search(request):
    run_flow_pipeline('pipeline_ml_with_grid_search')
    return HttpResponse("'pipeline_ml_with_grid_search' executed", status=200)

def trigger_pipeline_simple_with_celery(request):
    run_flow_pipeline('trigger_pipeline_simple_with_celery')
    return HttpResponse("'trigger_pipeline_simple_with_celery' executed", status=200)

def fetch_custom_ml_viz_data(request):

    ''' This is where you fetch or generate your data for visualization '''

    # These are the values in the dropdown
    executed_flow_id = request.GET.get('current_executed_flow_id')
    ml_result_id = request.GET.get('ml_result_option')
    if not ml_result_id or ml_result_id == '':
        return 'Cannot visualize nothing!'
    
    ml_result = mlops_models.MLResult.objects.get(pk=ml_result_id, executed_flow__id=executed_flow_id)
    metrics = ml_result.metrics
    charts = {}

    # Add metrics to the charts dict if they exist in your MLResult metrics
    if 'confusion_matrix' in metrics:
        charts['confusion_matrix'] = metrics['confusion_matrix']
    if 'accuracy_score' in metrics:
        charts['accuracy_score'] = metrics['accuracy_score']
    # Repeat for other metrics as necessary

    context = {'charts': charts,}

    return render(request, 'django_flow_forge/components/ml_result_chart.html', context)