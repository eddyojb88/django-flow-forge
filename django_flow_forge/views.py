from django.shortcuts import render
from . import models
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.shortcuts import render
import json
import logging

from django_flow_forge.task_utils import get_cytoscape_nodes_and_edges
from django_flow_forge.authorization import user_has_permission

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def conceptual_dag_viz(request,):

    if request.htmx:
        flow_option = request.GET.get('flow_option')
        flow = models.Flow.objects.get(id=flow_option)
        show_nested = switch_value_to_bool(request.GET.get('show_nested'))
        
    else:   
        flow = models.Flow.objects.all()[0]
        show_nested = False

    # Assuming FlowTask is your model and flow_name is a field in this model
    all_flows = models.Flow.objects.all()

    # Fetch all FlowTask instances for a given flow_name
    tasks = models.FlowTask.objects.filter(flow=flow,).prefetch_related('depends_on')
    if not show_nested:
        tasks = tasks.filter(nested=False)

    graph_json = get_cytoscape_nodes_and_edges(tasks, show_nested=show_nested)
    graph_json_serialized = json.dumps(graph_json, cls=DjangoJSONEncoder)

    context = {
        # 'plotly_fig': plot_div,  # The Plotly figure in HTML div format
        'graph_json': graph_json_serialized,
        'all_flowes': all_flows,
        'current_flow_id': flow.id,
    }

    if request.htmx:
        context = {'graph_json': graph_json_serialized, 'current_flow_id': flow.id}
        # Render a partial template with the new Cytoscape graph
        html = render_to_string('django_flow_forge/components/dag_cyto_conceptual_script.html', context=context )
        return HttpResponse(html)

    return render(request, 'django_flow_forge/dag_conceptual_index.html', context=context)

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def update_conceptual_node_info(request):

    if request.htmx:

        node_id = request.GET.get('clicked_node_id', None) # this is the id of the task it was when the task was first run
        flow_id = request.GET.get('executed_flow_option', None)
        context = {}
        if node_id:

            flow = models.Flow.objects.get(id=flow_id)

            if models.FlowTask.objects.filter(id=node_id, flow=flow).exists():

                task = models.FlowTask.objects.get(id=node_id, flow=flow)
                context['task'] = task

            else:
                logging.warning('No object found for this flow task.')


            return render(request, 'django_flow_forge/components/clicked_concept_node_info.html', context)
        
    return HttpResponse("Request must be made via HTMX.", status=400)


@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def tasks_run_viz(request):

    if request.htmx:
        flow_option = request.GET.get('executed_flow_option')
        executed_flow = models.ExecutedFlow.objects.get(id=flow_option)
        # show_nested = switch_value_to_bool(request.GET.get('show_nested'))
        
    else:   
        executed_flow = models.ExecutedFlow.objects.all().order_by('-start_time')[0]
        # show_nested = False

    # Assuming FlowTask is your model and flow_name is a field in this model
    all_executed_flowes = models.ExecutedFlow.objects.all().order_by('-start_time')
    flow_ml_results = models.MLResult.objects.filter(executed_flow=executed_flow)

    paginator = Paginator(all_executed_flowes, 10)  # Show 10 flowes per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch all FlowTask instances for a given flow_name
    # executed_tasks = models.ExecutedTask.objects.filter(flow_run=flow,)

    # if not show_nested:
    # executed_tasks = executed_tasks.filter(nested=False)

    graph_json = executed_flow.flow_snapshot['graph']
    graph_json_serialized = json.dumps(graph_json, cls=DjangoJSONEncoder)

    line_chart_data, pie_chart_data = summary_chart_view()

    context = {
        # 'plotly_fig': plot_div,  # The Plotly figure in HTML div format
        'graph_json': graph_json_serialized,
        'all_executed_flowes': all_executed_flowes,
        'page_obj': page_obj,
        'current_executed_flow_id': executed_flow.id,
        'ml_results': flow_ml_results,
        'line_chart_data': line_chart_data,
        'pie_chart_data': pie_chart_data,
    }

    if request.htmx:

        # Render a partial template with the new Cytoscape graph
        html = render_to_string('django_flow_forge/components/dag_graph_and_ml.html', context=context)
        return HttpResponse(html)

    return render(request, 'django_flow_forge/dag_tasks_run.html', context=context)

def summary_chart_view():
    # Aggregate tasks by day
    flowes_by_day = models.ExecutedFlow.objects.annotate(day=TruncDay('start_time')).values('day').annotate(count=Count('id')).order_by('day')
    
    # Prepare data for the line chart
    line_chart_data = {
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in flowes_by_day],
        'data': [entry['count'] for entry in flowes_by_day],
    }

    # Aggregate status breakdown
    status_breakdown = models.ExecutedFlow.objects.values('status').annotate(count=Count('status')).order_by('status')
    
    # Prepare data for the pie chart
    pie_chart_data = {
        'labels': [entry['status'] for entry in status_breakdown],
        'data': [entry['count'] for entry in status_breakdown],
    }

    line_chart_data = json.dumps(line_chart_data, cls=DjangoJSONEncoder)
    pie_chart_data = json.dumps(pie_chart_data, cls=DjangoJSONEncoder)
    
    return line_chart_data, pie_chart_data

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def update_task_run_node_info(request):

    if request.htmx:

        node_id = request.GET.get('clicked_node_id', None) # this is the id of the task it was when the task was first run
        executed_flow_id = request.GET.get('current_executed_flow_option', None)

        context = {}

        if node_id:

            if models.ExecutedTask.objects.filter(task_snapshot_id=node_id, flow_run_id=executed_flow_id).exists():

                executed_task = models.ExecutedTask.objects.get(task_snapshot_id=node_id, flow_run_id=executed_flow_id)
                executed_task_summary = {}
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
                ml_results = models.MLResult.objects.filter(executed_flow_id=executed_flow_id)
                context['ml_result_count'] = len(ml_results)
                context['ml_results'] = ml_results

            else:
                logging.warning('No object found for this flow task.')


            return render(request, 'django_flow_forge/components/clicked_executed_task_node_info.html', context)
        
    return HttpResponse("Request must be made via HTMX.", status=400)

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def display_ml_results_table(request):

    executed_flow_id = request.GET.get('current_executed_flow_id')
    ml_result_id = request.GET.get('ml_result_option')
    
    if ml_result_id and ml_result_id != '':
        ml_result = models.MLResult.objects.get(pk=ml_result_id, executed_flow__id=executed_flow_id)
    else:
        ml_result = None

    context = {'ml_result': ml_result,
               'current_executed_flow_id': executed_flow_id,}
    
        
    return render(request, 'django_flow_forge/components/ml_result.html', context)

@user_has_permission(permission='django_flow_forge.django_flow_admin_access')
def fetch_ml_viz_data(request):
    # This is where you fetch or generate your data for visualization
    executed_flow_id = request.GET.get('current_executed_flow_id')
    ml_result_id = request.GET.get('ml_result_option')
    ml_result = models.MLResult.objects.get(pk=ml_result_id, executed_flow__id=executed_flow_id)
    metrics = ml_result.metrics
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