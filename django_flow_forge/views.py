from django.shortcuts import render
from . import models
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from datetime import datetime
from django.db.models.functions import TruncDay
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
import json
import re
import logging

from django_flow_forge.task_utils import get_cytoscape_nodes_and_edges
from django_flow_forge.authorization import user_has_permission

POSTS_PER_PAGE = 12

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def conceptual_dag_viz(request,):

    if request.htmx:
        pipeline_option = request.GET.get('pipeline_option')
        pipeline = models.Pipeline.objects.get(id=pipeline_option)
        
    else:   
        from django_flow_forge.auto_register_pipelines import auto_register_pipelines
        print('Auto discovering tasks from fresh')
        auto_register_pipelines()
        pipeline = models.Pipeline.objects.all()[0]

    # Assuming PipelineTask is your model and pipeline_name is a field in this model
    all_pipelines = models.Pipeline.objects.all()

    # Fetch all PipelineTask instances for a given pipeline_name
    tasks = models.PipelineTask.objects.filter(pipeline=pipeline,).prefetch_related('depends_on')

    graph_json = get_cytoscape_nodes_and_edges(tasks,)
    graph_json_serialized = json.dumps(graph_json, cls=DjangoJSONEncoder)

    context = {
        # 'plotly_fig': plot_div,  # The Plotly figure in HTML div format
        'graph_json': graph_json_serialized,
        'all_pipelines': all_pipelines,
        'current_pipeline_id': pipeline.id,
    }

    if request.htmx:
        context = {'graph_json': graph_json_serialized, 'current_pipeline_id': pipeline.id}
        # Render a partial template with the new Cytoscape graph
        html = render_to_string('django_flow_forge/components/dag_cyto_conceptual_script.html', context=context )
        return HttpResponse(html)

    return render(request, 'django_flow_forge/dag_conceptual_index.html', context=context)

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def update_conceptual_node_info(request):

    if request.htmx:

        node_id = request.GET.get('clicked_node_id', None) # this is the id of the task it was when the task was first run
        pipeline_id = request.GET.get('executed_pipeline_option', None)
        context = {}
        if node_id:

            pipeline = models.Pipeline.objects.get(id=pipeline_id)

            if models.PipelineTask.objects.filter(id=node_id, pipeline=pipeline).exists():

                task = models.PipelineTask.objects.get(id=node_id, pipeline=pipeline)
                context['task'] = task

            else:
                logging.warning('No object found for this pipeline task.')


            return render(request, 'django_flow_forge/components/clicked_concept_node_info.html', context)
        
    return HttpResponse("Request must be made via HTMX.", status=400)

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def search_pipeline_runs(request):
    context = {}
    if request.htmx:
        context['searched_pipelines'], context['search'] = _search_posts(request)
        return render(request, "django_flow_forge/components/table_search_results.html", context)
        
    return HttpResponse("Request must be made via HTMX.", status=400)

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def tasks_run_viz(request):

    context = {}

    if request.htmx:
        pipeline_option = request.GET.get('executed_pipeline_option')
        executed_pipeline = models.ExecutedPipeline.objects.get(id=pipeline_option)
        # show_nested = switch_value_to_bool(request.GET.get('show_nested'))
        
    else:   
        executed_pipeline = models.ExecutedPipeline.objects.all().order_by('-start_time')[0]
        # show_nested = False

    # Assuming PipelineTask is your model and pipeline_name is a field in this model
    all_executed_pipelines = models.ExecutedPipeline.objects.all().order_by('-start_time')
    pipeline_ml_results = models.MLResult.objects.filter(executed_pipeline=executed_pipeline)
    
    context['searched_pipelines'], context['search'] = _search_posts(request)

    paginator = Paginator(all_executed_pipelines, 10)  # Show 10 pipelinees per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch all PipelineTask instances for a given pipeline_name
    # executed_tasks = models.ExecutedTask.objects.filter(pipeline_run=pipeline,)

    # if not show_nested:
    # executed_tasks = executed_tasks.filter(nested=False)
    try:
        graph_json = executed_pipeline.pipeline_snapshot['graph']
        graph_json_serialized = json.dumps(graph_json, cls=DjangoJSONEncoder)
        context['graph_json'] = graph_json_serialized

    except Exception as e:
        pass

    line_chart_data, pie_chart_data = summary_chart_view()

    
        # 'plotly_fig': plot_div,  # The Plotly figure in HTML div format
    
    context['all_executed_pipelines'] = all_executed_pipelines
    context['page_obj'] = page_obj
    context['current_executed_pipeline_id'] = executed_pipeline.id
    context['ml_results'] = pipeline_ml_results
    context['ml_results_count'] = len(pipeline_ml_results)
    context['line_chart_data'] = line_chart_data
    context['pie_chart_data'] = pie_chart_data

    if request.htmx:

        # Render a partial template with the new Cytoscape graph
        html = render_to_string('django_flow_forge/components/dag_graph_and_ml.html', context=context)
        return HttpResponse(html)

    return render(request, 'django_flow_forge/dag_tasks_run.html', context=context)

def _search_posts(request):
    search = request.GET.get("search")
    page = request.GET.get("page")
    posts = models.ExecutedPipeline.objects.all()

    if search:
        tokens = search.split()
        combined_query = Q()

        for token in tokens:
            token_query = Q()

            # General search for pipeline_name
            token_query |= Q(pipeline_name_snapshot__icontains=token)

            # Check if the token matches a date format (month-year)
            date_match = re.match(r"(\d{4})-(\d{2})", token)
            if date_match:
                year, month = date_match.groups()
                token_query |= Q(start_time__year=year, start_time__month=month)

            # Search within the JSONField `meta` for a specific label
            token_query |= Q(meta__icontains=token)

            combined_query &= token_query

        posts = posts.filter(combined_query)
    
    posts = posts.order_by('-start_time')

    paginator = Paginator(posts, POSTS_PER_PAGE)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return posts, search or ""

def summary_chart_view():
    # Aggregate tasks by day
    pipelines_by_day = models.ExecutedPipeline.objects.annotate(day=TruncDay('start_time')).values('day').annotate(count=Count('id')).order_by('day')
    
    # Prepare data for the line chart
    line_chart_data = {
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in pipelines_by_day],
        'data': [entry['count'] for entry in pipelines_by_day],
    }

    # Aggregate status breakdown
    status_breakdown = models.ExecutedPipeline.objects.values('status', 'start_time').annotate(count=Count('status')).order_by('status')

    
    # Prepare data for the pie chart
    # pie_chart_data = {
        # 'labels': [entry['status'] for entry in status_breakdown],
        # 'data': [entry['count'] for entry in status_breakdown],
    # }

    pie_chart_data = {
        'labels': list(set([entry['status'] for entry in status_breakdown])),
        'data': [{'status': entry['status'], 'count': entry['count'], 
                  'start_time': entry['start_time'].strftime('%Y-%m-%d')} for entry in status_breakdown],
    }

    line_chart_data = json.dumps(line_chart_data, cls=DjangoJSONEncoder)
    pie_chart_data = json.dumps(pie_chart_data, cls=DjangoJSONEncoder)
    
    return line_chart_data, pie_chart_data

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def update_task_run_node_info(request):

    if not request.htmx:
        return HttpResponse("Request must be made via HTMX.", status=400)
    
    node_id = request.GET.get('clicked_node_id', None) # this is the id of the task it was when the task was first run
    executed_pipeline_id = request.GET.get('current_executed_pipeline_option', None)

    context = {}

    if not node_id:
        return HttpResponse("Bad request.", status=400)

    if not models.ExecutedTask.objects.filter(task_snapshot_id=node_id, pipeline_run_id=executed_pipeline_id).exists():
        return HttpResponse("Bad request.", status=400)

    executed_task = models.ExecutedTask.objects.get(task_snapshot_id=node_id, pipeline_run_id=executed_pipeline_id)
    executed_task_summary = {}
    if not executed_task.task:
        executed_task_summary['task_name'] = executed_task.task_snapshot['task_name']
    else:
        executed_task_summary['task_name'] = executed_task.task.task_name 

    executed_task_summary['Task Status'] = executed_task.status
    executed_task_summary['Start Time'] = executed_task.start_time
    executed_task_summary['End Time'] = executed_task.end_time

    if executed_task.status == 'failed':
        executed_task_summary['Exception'] = executed_task.exceptions['main_run']
        context['code_in_response'] = True

    else:    
        executed_task_summary['Output'] = executed_task.output
    
    context['executed_task_summary'] = executed_task_summary

    ''' Check if any machine learning experiments associated with node'''
    ml_results = models.MLResult.objects.filter(executed_pipeline_id=executed_pipeline_id)
    context['ml_result_count'] = len(ml_results)
    context['ml_results'] = ml_results

    return render(request, 'django_flow_forge/components/clicked_executed_task_node_info.html', context)
        
@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def display_ml_results_table(request):

    executed_pipeline_id = request.GET.get('current_executed_pipeline_id')
    ml_result_id = request.GET.get('ml_result_option')
    
    if ml_result_id and ml_result_id != '':
        ml_result = models.MLResult.objects.get(pk=ml_result_id, executed_pipeline__id=executed_pipeline_id)
    else:
        ml_result = None

    context = {'ml_result': ml_result,
               'current_executed_pipeline_id': executed_pipeline_id,}
    
        
    return render(request, 'django_flow_forge/components/ml_result.html', context)

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def fetch_ml_viz_data(request):
    # This is where you fetch or generate your data for visualization
    executed_pipeline_id = request.GET.get('current_executed_pipeline_id')
    ml_result_id = request.GET.get('ml_result_option')
    ml_result = models.MLResult.objects.get(pk=ml_result_id, executed_pipeline__id=executed_pipeline_id)
    metrics = ml_result.evaluation_metrics
    charts = {}

    # Add metrics to the charts dict if they exist in your MLResult metrics
    if 'confusion_matrix' in metrics:
        charts['confusion_matrix'] = metrics['confusion_matrix']
    if 'accuracy_score' in metrics:
        charts['accuracy_score'] = metrics['accuracy_score']
    # Repeat for other metrics as necessary

    context = {'charts': charts}

    return render(request, 'django_flow_forge/components/ml_result_chart.html', context)

def switch_value_to_bool(switch):

    if not switch:
        return False

    if type(switch) == list:
        switch = switch[0]

    if switch and switch == 'on':
        switch = True

    else:
        switch=False

    return switch