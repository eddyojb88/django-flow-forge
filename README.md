[![codecov](https://codecov.io/gh/eddyojb88/django_mlops/graph/badge.svg?token=J1V3STRJLZ)](https://codecov.io/gh/eddyojb88/django_mlops)

# django_mlops
 Utilities for Data Scientists and Engineers looking to simplify ML Ops without unnecessary complexity.

## Motivation?
Philosophy:

An ML system should be simple enough that an ops colleague can 

(1) Find out when it isn’t working properly

(2) Make small changes to it

(3) Redeploy the model

The problem with todays tools is that they feel like learning enormous packages with fancy webserves and a lot of bloat without solving the problems flexibly, This was the motivation behind Django-mlops - in our teams case it solves it all end to end.

MLOps sounds like a made up sales term. However, it is necessary in data science projects to:

- Design and keep track of data science projects in a way that can be communicated easily to team members and stakeholders easily
- Offer optional scalability in data ops or model training in order to find solutions to complex problems

Key Features:
- Simple and mature framework with Django philosophy of robustness with safety and security
- Definition of pipelines processes in a data science context (but it is flexible to work in any context)
- Visualization of DAGs, doubling up as a tool for stakeholder interactions (inspired by Kedro)
- To do: Connectors to e.g. Celery in order to run DAGs using dependencies
- Scalable archtecture, working with Celery nicely or Kubernetes. Like any project ever, this requires design and implementation


Why Django and not Flask, FastAPI etc.
- Opinions are important, especially if they help your app stay secure and manageable. Flask and FastAPI is supposed to be lightweight but every project I go on ends up recreating logic that Django already has but badly and closed sourced. Why not skip the duplication and complexity?
- Django is easy to deploy Dockerize securely and scalably on any cloud service, keeping your options flexible
- Django-ninja is FastAPI for Django, offering a fast way to serve models in a coupled or decoupled manner
- Move fast by start off your project simple with django and decouple as and when you need. As you scale, your app in Django doesnt necessarily need to be rewritten

