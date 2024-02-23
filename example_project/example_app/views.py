from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from django_mlops.tasks_db import run_process_pipeline

from . import tasks_and_pipeline # This is important in order to load up your tasks and allow the model to register each task

# from . import tasks_with_decorators # This is important in order to load up your tasks and allow the model to register each task

def index(request):
    return render(request, 'example_app/index.html')

def trigger_data_science_proj1(request):

    run_process_pipeline('data_science_project_simple')
    # Assuming you have some mechanism to detect when tasks are done,
    # you can then do something here or just return a simple HttpResponse.
    return HttpResponse("Tasks executed", status=200)

def trigger_data_science_proj1_with_nested(request):

    run_process_pipeline('data_science_project_with_nesting')
    # Assuming you have some mechanism to detect when tasks are done,
    # you can then do something here or just return a simple HttpResponse.
    return HttpResponse("Tasks executed", status=200)