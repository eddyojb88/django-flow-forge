# Flow Dashboard

## Features


<img width="1057" alt="Screenshot 2024-02-27 at 11 45 02" src="https://github.com/eddyojb88/django-flow-forge/assets/22086433/36e80d55-4968-40e1-bf73-9eaef5247a8f">

- Task monitoring (there is auto-checkpoints between Tasks)
- Visualize a Flow in terms of its Tasks, dependecy tree and Task status. Clicking on nodes allows you to inspect the status and output

- Outputs for your machine learning algorithms

You are required to define what the machine learning outputs are, which are saved to the MLResults object.

At the moment, this aspect is hands off, recognising that the world of ML is rapidly changing and that different domains require different evaluation metrics recorded. This is why this aspect intends to be replaceable and extensible. With Django-HTMX, chart.js and a bit of Chatgpt, it is very simple to code a visualisation.