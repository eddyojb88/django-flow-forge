from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

# from example_app import pipelines
from example_app.pipelines.simple_example_with_celery import SimpleWithCelery
from example_app.pipelines.celery_with_parallel_pipelines import SimpleWithCeleryParallel

def index(request):
    return render(request, 'example_app/index.html')

def trigger_pipeline_simple(request):
    from example_app.pipelines.simple_example import SimplePipeline
    SimplePipeline().run()
    return HttpResponse("'Pipeline Simple' Executed", status=200)

def trigger_pipeline_simple_with_fail(request):
    from example_app.pipelines.simple_example_with_failure import SimplePipelineFail
    SimplePipelineFail().run()
    return HttpResponse("'Pipeline Simple with Failure' Executed", status=200)

def trigger_pipeline_ml_grid_search(request):
    from example_app.pipelines.ml_grid_search_example import MLGridSearchPipeline
    MLGridSearchPipeline().run()
    return HttpResponse("'pipeline_ml_with_grid_search' executed", status=200)

def trigger_pipeline_simple_with_celery(request):
    SimpleWithCelery().run()
    return HttpResponse("'trigger_pipeline_simple_with_celery' executed", status=200)

def trigger_pipeline_parallel_with_celery(request):
    SimpleWithCeleryParallel().run(use_celery=True)
    return HttpResponse("'pipeline_in_parallel_with_celery' executed", status=200)

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