# django_mlops
 MLOps Utilities for Data Scientists and Engineers

## Motivation?
MLOps sounds like a fad and in a lot of cases it appears unnecessary. However, it is necessary in data science projects to:
- Design and keep track of data science projects in a way that can be communicated easily to team members and stakeholders easily
- Offer optional scalability in data ops or model training in order to find solutions to complex problems

To be blunt, most open source MLOps tools out there are fancy webservers with some monitoring or execution logic. There are many frameworks, such as Kedro, Apache Airflow, Kubeflow, Luigi with GoKart etc. However, none of them tick all of the boxes and they all reinvent components already developed in DevOps or web development frameworks with an extra sprinkling of logic relevant to Data Science.

Has this community lost its way? I felt so and this framework is an attempt to simplify the process, going back to simple but mature web and data friendly frameworks, adding some simple, robust and extensible modelling with a lightweight but effective visualisation tool that was inspired by Kedro.

Key Features:
- Decorators to track lineage of data processing tasks using nodes in a Directed Acyclic Graph (DAG) - Kedro excels at this
- Visualization of DAGs, doubling up as a tool for stakeholder interactions
- To do: Connectors to e.g. Celery in order to run DAGs using dependencies


Why Django and not Flask, FastAPI etc.
- Django-ninja is FastAPI for Django
- Opinions are important, especially if they help your app stay secure and manageable. Flask and FastAPI is supposed to be lightweight but every project I go on ends up recreating logic that Django already has but badly and closed sourced. Why not skip the duplication and complexity?
- Django is easy to deploy Dockerize securely and scalably on any cloud service, keeping your options flexible

