# Data Science Experiments

## Storing Results from Data Science Experiments

You can view examples for this in the ```ml_grid_search.py``` script.

Results are stored to JSON fields within the database using the Task object.

These results are automatically viewable in the dashboard.

## Visualizations of Data Science Experiments
Only the table of results is displayed in the Pipeline Monitor page ```localhost:8000/django_flow_forge/task-runs-viz```
but you can easily create your own visualisation page in Django by reading from the relevant Task objects for given Flows of interest.

Data science experiments can easily be plotted by extracting results from the MLResults model in django_flow_forge 
```from django_flow_forge.models import MLResult```and you can send the data to the view template and render using something like Plotly or echarts. This is easily achieved using a Copilot.