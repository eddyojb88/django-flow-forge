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

from django_mlops.task_utils import get_cytoscape_nodes_and_edges

def conceptual_dag_viz(request,):

    if request.htmx:
        process_option = request.GET.get('process_option')
        process = models.Process.objects.get(id=process_option)
        show_nested = switch_value_to_bool(request.GET.get('show_nested'))
        
    else:   
        process = models.Process.objects.all()[0]
        show_nested = False

    # Assuming ProcessTask is your model and process_name is a field in this model
    all_processes = models.Process.objects.all()

    # Fetch all ProcessTask instances for a given process_name
    tasks = models.ProcessTask.objects.filter(process=process,).prefetch_related('depends_on')
    if not show_nested:
        tasks = tasks.filter(nested=False)

    graph_json = get_cytoscape_nodes_and_edges(tasks, show_nested=show_nested)
    graph_json_serialized = json.dumps(graph_json, cls=DjangoJSONEncoder)

    context = {
        # 'plotly_fig': plot_div,  # The Plotly figure in HTML div format
        'graph_json': graph_json_serialized,
        'all_processes': all_processes,
    }

    if request.htmx:

        # Render a partial template with the new Cytoscape graph
        html = render_to_string('django_mlops/components/dag_cyto_conceptual.html', {'graph_json': graph_json_serialized})
        return HttpResponse(html)

    return render(request, 'django_mlops/dag_conceptual_index.html', context=context)

def tasks_run_viz(request):

    if request.htmx:
        process_option = request.GET.get('executed_process_option')
        executed_process = models.ExecutedProcess.objects.get(id=process_option)
        # show_nested = switch_value_to_bool(request.GET.get('show_nested'))
        
    else:   
        executed_process = models.ExecutedProcess.objects.all().order_by('-start_time')[0]
        # show_nested = False

    # Assuming ProcessTask is your model and process_name is a field in this model
    all_executed_processes = models.ExecutedProcess.objects.all().order_by('-start_time')
    process_ml_results = models.MLResult.objects.filter(executed_process=executed_process)

    paginator = Paginator(all_executed_processes, 10)  # Show 10 processes per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch all ProcessTask instances for a given process_name
    # executed_tasks = models.ExecutedTask.objects.filter(process_run=process,)

    # if not show_nested:
    # executed_tasks = executed_tasks.filter(nested=False)

    graph_json = executed_process.process_snapshot['graph']
    graph_json_serialized = json.dumps(graph_json, cls=DjangoJSONEncoder)

    line_chart_data, pie_chart_data = summary_chart_view()

    context = {
        # 'plotly_fig': plot_div,  # The Plotly figure in HTML div format
        'graph_json': graph_json_serialized,
        'all_executed_processes': all_executed_processes,
        'page_obj': page_obj,
        'current_executed_process_id': executed_process.id,
        'ml_results': process_ml_results,
        'line_chart_data': line_chart_data,
        'pie_chart_data': pie_chart_data,
    }

    if request.htmx:

        # Render a partial template with the new Cytoscape graph
        html = render_to_string('django_mlops/components/dag_graph_and_ml.html', context=context)
        return HttpResponse(html)

    return render(request, 'django_mlops/dag_tasks_run.html', context=context)

def summary_chart_view():
    # Aggregate tasks by day
    processes_by_day = models.ExecutedProcess.objects.annotate(day=TruncDay('start_time')).values('day').annotate(count=Count('id')).order_by('day')
    
    # Prepare data for the line chart
    line_chart_data = {
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in processes_by_day],
        'data': [entry['count'] for entry in processes_by_day],
    }

    # Aggregate status breakdown
    status_breakdown = models.ExecutedProcess.objects.values('status').annotate(count=Count('status')).order_by('status')
    
    # Prepare data for the pie chart
    pie_chart_data = {
        'labels': [entry['status'] for entry in status_breakdown],
        'data': [entry['count'] for entry in status_breakdown],
    }

    line_chart_data = json.dumps(line_chart_data, cls=DjangoJSONEncoder)
    pie_chart_data = json.dumps(pie_chart_data, cls=DjangoJSONEncoder)
    
    return line_chart_data, pie_chart_data

def update_node_info(request):

    if request.htmx:

        node_id = request.GET.get('clicked_node_id', None) # this is the id of the task it was when the task was first run
        executed_process_id = request.GET.get('current_executed_process_option', None)

        if node_id:

            executed_process = models.ExecutedProcess.objects.get(id=executed_process_id)

            if models.ExecutedTask.objects.filter(task_snapshot_id=node_id, process_run=executed_process).exists():

                executed_task = models.ExecutedTask.objects.get(task_snapshot_id=node_id, process_run=executed_process)
                executed_task_summary = {}
                executed_task_summary['Task Status'] = executed_task.status
                executed_task_summary['Start Time'] = executed_task.start_time
                executed_task_summary['End Time'] = executed_task.end_time

                if executed_task.status == 'failed':
                    executed_task_summary['Exception'] = executed_task.exceptions

                else:    
                    executed_task_summary['Output'] = executed_task.output
                
                context = {'executed_task_summary': executed_task_summary}

                ''' Check if any machine learning experiments associated with node'''
                ml_results = models.MLResult.objects.filter(executed_process=executed_process)
                context['ml_result_count'] = len(ml_results)
                context['ml_results'] = ml_results

            else:
                logging.warning('No object found for this process task.')


            return render(request, 'django_mlops/components/clicked_node_info.html', context)
        
    return HttpResponse("Request must be made via HTMX.", status=400)

def display_ml_results_table(request):

    executed_process_id = request.GET.get('current_executed_process_id')
    ml_result_id = request.GET.get('ml_result_option')
    
    if ml_result_id and ml_result_id != '':
        ml_result = models.MLResult.objects.get(pk=ml_result_id, executed_process__id=executed_process_id)
    else:
        ml_result = None

    context = {'ml_result': ml_result,
               'current_executed_process_id': executed_process_id,}
    
        
    return render(request, 'django_mlops/components/ml_result.html', context)

def fetch_ml_viz_data(request):
    # This is where you fetch or generate your data for visualization
    executed_process_id = request.GET.get('current_executed_process_id')
    ml_result_id = request.GET.get('ml_result_option')
    ml_result = models.MLResult.objects.get(pk=ml_result_id, executed_process__id=executed_process_id)
    metrics = ml_result.metrics
    charts = {}

    # Add metrics to the charts dict if they exist in your MLResult metrics
    if 'confusion_matrix' in metrics:
        charts['confusion_matrix'] = metrics['confusion_matrix']
    if 'accuracy_score' in metrics:
        charts['accuracy_score'] = metrics['accuracy_score']
    # Repeat for other metrics as necessary

    context = {'charts': charts}

    return render(request, 'django_mlops/components/ml_result_chart.html', context)

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