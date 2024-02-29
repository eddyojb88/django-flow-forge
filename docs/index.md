# Welcome to Django ML Ops

Ignore the ML Ops salesmen and get back to keeping your ML system simple, flexible and impactful with this handy plugin module for Django, aimed at Data Scientists and Data Engineers looking to standardize but simplify their tech stack and not get sucked in to development paralysis from vendor lock-in or the tech stack complexity that other projects feature.

# Features

- Define your pipeline processes (DAGs) simply
- Stakeholder facing visualization of your pipeline DAG in concept before and during development
- Register and execute your pipelines using either a standalone script or use Django website or via a speedy Django-ninja API
- Task monitoring
- Visualise pipeline process outputs and failures for each task
- Display data science experiment results for comparison
- Serve models with DRF or Django Ninja (FastAPI for Django)
- Minimal learning if you already know Django
- Using this with Django means you are not bogged down worrying about security, scalabili
- Scalable with Django Celery or Kuberenetes or any other extension you want to use
- Django is a mature framework with lots of security features if you want to serve models 
- No vendor lockin

# Motivation

This package is inspired by the following articles that either discuss or show cyncisism towards MLOps:

- [Do you need ML Ops](https://medium.com/@eddyojb/thoughts-you-wont-get-from-chatgpt-do-you-need-ml-ops-2c954b9d47a6)
- [No, you dont need ML Ops](https://becominghuman.ai/no-you-dont-need-mlops-5e1ce9fdaa4b)
- [I dont like Notebooks/Collab](https://www.youtube.com/watch?v=7jiPeIFXb6U)

## Philosophy:

It is necessary in data science projects to:

- Design and keep track of data science projects in a way that can be easily communicated to team members and stakeholders
- Offer scalability when gathering data or model training in order to find (much) better solutions to complex problems

An ML system should also be simple enough that an ops colleague can:

(1) Find out when it isn’t working properly

(2) Make small changes to it

(3) Redeploy the model

In most cases, we probably don't need any of the ML Ops tools out there. Lets also face reality that in a lot of cases, the problems can be attributed to bad or zero code design and the use of notebooks.

## The State of the ML Ops ecosystem
The open source tools are a mess and vendor solutions generally unsuitable and expensive without having what is required to get your project done well, quickly and extensibly. They all appear to be packages with fancy webservers or a lot of bloat without solving the problem flexibly and robustly, which became the inspiration for Django ML Ops.

Lets quantify that statement e.g. the Kedro and Kedro-viz repos have about approx. 430k lines of code. 80% of that is the React based viz and its associated assets. However, django_mlops has <3k lines of code and it is understood that it can achieve the same features and more. See the features list which describes why this module ticks all boxes for our team.