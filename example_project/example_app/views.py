from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from django_mlops.tasks_db import run_process_pipeline

 # This is important in order to load up your tasks and allow django_ml_ops to register each task
from . import pipeline_simple, pipeline_with_nested_tasks, pipeline_simple_ml, pipeline_ml_grid_search 

def index(request):
    return render(request, 'example_app/index.html')

def trigger_pipeline_simple(request):
    run_process_pipeline('pipeline_simple')
    return HttpResponse("'Pipeline Simple' Executed", status=200)

def trigger_pipeline_with_nested_tasks(request):
    run_process_pipeline('pipeline_with_nested_tasks')
    return HttpResponse("'pipeline_with_nested_tasks' executed", status=200)

def trigger_pipeline_simple_ml(request):
    run_process_pipeline('pipeline_simple_ml')
    return HttpResponse("'pipeline_simple_ml' executed", status=200)

def trigger_pipeline_ml_grid_search(request):
    run_process_pipeline('pipeline_ml_grid_search')
    return HttpResponse("'pipeline_ml_grid_search' executed", status=200)