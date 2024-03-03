# Data Science Experiments

## Storing Results from Data Science Experiments

You can view examples for this in the ```flow__simple_ml.py``` and ```flow__ml_grid_search.py``` scripts.

Results are stored to JSON fields within the database using the Task object.

These results are automatically viewable in the dashboard.

## Visualizations of Data Science Experiments
This is currently in development. However, you can easily create your own visualisation page in Django by reading from the relevant Task objects for given Flows of interest.

Data science experiments can be plotted using Plotly, Bokeh and sending these through a Django view to a template, or send the data through the view and visualise in chart.js (use ChatGPT / Copilot etc, to help you write this.)

It is intended that more visualisation options will be included in the module and documented.