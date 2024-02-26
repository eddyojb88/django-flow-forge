[![codecov](https://codecov.io/gh/eddyojb88/django_mlops/graph/badge.svg?token=J1V3STRJLZ)](https://codecov.io/gh/eddyojb88/django_mlops)

# django_mlops
 Utilities for Data Scientists and Engineers looking to simplify ML Ops without unnecessary complexity.

# Motivation

## Philosophy:

An ML system should be simple enough that an ops colleague can 

(1) Find out when it isn’t working properly

(2) Make small changes to it

(3) Redeploy the model

MLOps sounds like a made up sales term. However, it is necessary in data science projects to:

- Design and keep track of data science projects in a way that can be communicated easily to team members and stakeholders easily
- Offer optional scalability in data ops or model training in order to find solutions to complex problems
  
## The problem with the ML Ops ecosystem
There is no need to learn any of the enormous packages associated with ML Ops, such as Kedro, KubeFlow, Metaflow etc. Even vendor solutions, such as DataBricks. They are all packages with fancy webserves and a lot of bloat without solving the problems they set out to flexibly and robustly, which became the inspiration for Django ML Ops.

## Key Features:
- Simple and mature framework with Django philosophy of robustness with safety and security
- Flexible in defining pipelines of tasks with or without a data science context
- Doesn't tie developers down to any scaling method - the repo includes an example with Celery and RabbbitMQ but it should also scale nicely to Kubernetes or any other package if required
- Visualization of DAGs, doubling up as a tool for stakeholder interactions (inspired by Kedro)

 ## Features to come
 - Implement better authentication and authorization options (at the moment you have to import the views in to urls and add login_required
 - Async capability: allow user to use the dependency tree in the graph in order to wait for relevant tasks that have been offloaded to complete
 - Make stakeholder only facing dashboard to display only tasks that succeeded


## Why Django and not Flask, FastAPI etc.
- Flask and FastAPI are great for starting out as they appear simple. However, every project that uses these tools ends up recreating logic that Django already has but badly and closed sourced. Why duplicate and add complexity?
- Django is realtively simple to deploy with Docker securely and scalably on any cloud service, keeping options flexible
- Django-ninja is FastAPI for Django, offering a fast way to serve models in a coupled or decoupled manner
- Move fast by starting off your project simple with django and decouple as and when you need. As you scale, your app in Django doesnt necessarily need to be rewritten

