from django.shortcuts import render
from . import models
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
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
        'process_data': graph_json_serialized,
        'all_processes': all_processes,
    }

    if request.htmx:

        # Render a partial template with the new Cytoscape graph
        html = render_to_string('django_mlops/components/cyto_container.html', {'process_data': graph_json_serialized})
        return HttpResponse(html)

    return render(request, 'django_mlops/dag_conceptual_index.html', context=context)

def tasks_run_viz(request):

    return

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