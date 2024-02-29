# django_mlops

!!! Docs in progress. Check back in a couple of days. !!!

Ignore the ML Ops salesmen and get back to keeping your ML system simple, flexible and impactful with this handy plugin module for Django.

This module is for Architects, Data Scientists and Data Engineers looking to save time in the long term by standardizing and simplifying their tech stack, not getting sucked in to vendor lock-in or tech stack complexity when they hit they realise the other packages don't have what they need.

![mlops_gif](https://github.com/eddyojb88/django_mlops/assets/22086433/9ea13500-2019-4145-995f-1fd855f51c74)

# Motivation

[Read the Docs](https://eddyojb88.github.io/django_mlops/) for more info on this


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

 ## Features to come
 - Documentation page
 - Implement better authentication and authorization options (at the moment you have to import the views in to urls and add login_required
 - Async capability: allow user to use the dependency tree in the graph in order to wait for relevant tasks that have been offloaded to complete
 - Make stakeholder only facing dashboard to display only tasks that succeeded

# Quick Start

Docs are here: [Read the Docs](https://eddyojb88.github.io/django_mlops/).

```
docker compose -f docker-compose-local.yml up
```

This runs both a Django container and a RabbitMQ container for the async task example with celery.

Next, connect in to the Django docker container.

There are a series of examples to showcase functionality, mostly without async. If you are not yet interested in async, you can skip the next part but if you are then within the ```example_project``` directory, run:

```
celery -A example_app  worker --loglevel=info
```

This starts the celery instance for the example async task.

Next, run the django server with:

```
python manage.py runserver  0.0.0.0:8000
```

With the development server now running, you can view the list of trigger examples at:

```
http://localhost:8005/example/
```

In order to understand how this is being run, you can view the associated scripts in the ```example_app``` directory,
with ```pipeline_simple.py``` being the simplest example to view how a pipeline is registered. To view how the pipeline is called, go to ```views.py``` and the ```trigger_pipeline_simple``` function.

Once the task is complete, you can view the pipeline summary and associated info at the following page:

```
http://localhost:8005/django_mlops/task-runs-viz/
```

If wanting to conceptualize a task for stakeholders before or during development, you can view the pipeline in concept by going to:

```
http://localhost:8005/django_mlops/conceptual-dag-viz/

<img width="1057" alt="Screenshot 2024-02-27 at 11 45 02" src="https://github.com/eddyojb88/django_mlops/assets/22086433/36e80d55-4968-40e1-bf73-9eaef5247a8f">