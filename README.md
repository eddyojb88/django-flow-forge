[![codecov](https://codecov.io/gh/eddyojb88/django_mlops/graph/badge.svg?token=J1V3STRJLZ)](https://codecov.io/gh/eddyojb88/django_mlops)

# django_mlops
A module for Data Scientists and Engineers looking to standardize and simplify ML Ops without the unnecessary complexity.

![mlops_gif](https://github.com/eddyojb88/django_mlops/assets/22086433/9ea13500-2019-4145-995f-1fd855f51c74)


# Quick Start (Documentation site coming soon.)

1) It is assumed that you are familiar with Docker. An alternative is to use the requirements file in your own python environment and skip to Step 3.

```
docker compose -f docker-compose-local.yml up
```

This runs both a Django container and a RabbitMQ container for the async task example with celery.

2) Next, connect to the Django docker container either with e.g. VSCode or terminal:

 ```
docker exec -it <your_container_id> bash 
 ```

3) There are a series of examples to showcase functionality, mostly without async. If you are not yet interested in async, you can skip the next part but if you are then within the ```example_project``` directory, run:

```
celery -A example_app  worker --loglevel=info
```

This starts the celery instance for the example async task.

4) Next, run the django server with:

```
python manage.py runserver  0.0.0.0:8000
```

5) With the development server now running, you can view the list of trigger examples at:

```
http://localhost:8005/example/
```

6) In order to understand how this is being run, you can view the associated scripts in the ```example_app``` directory,
with ```pipeline_simple.py``` being the simplest example to view how a pipeline is registered. To view how the pipeline is called, go to ```views.py``` and the ```trigger_pipeline_simple``` function.

7) Once the task is complete, you can view the pipeline summary and associated info at the following page:

```
http://localhost:8005/django_mlops/task-runs-viz/
```

8) If wanting to conceptualize a task for stakeholders before or during development, you can view the pipeline in concept by going to:

```
http://localhost:8005/django_mlops/conceptual-dag-viz/
```

<img width="1057" alt="Screenshot 2024-02-27 at 11 45 02" src="https://github.com/eddyojb88/django_mlops/assets/22086433/36e80d55-4968-40e1-bf73-9eaef5247a8f">

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
 - Documentation page
 - Implement better authentication and authorization options (at the moment you have to import the views in to urls and add login_required
 - Async capability: allow user to use the dependency tree in the graph in order to wait for relevant tasks that have been offloaded to complete
 - Make stakeholder only facing dashboard to display only tasks that succeeded


## Why Django and not Flask, FastAPI etc.
- Flask and FastAPI are great for starting out as they appear simple. However, every project that uses these tools ends up recreating logic that Django already has but badly and closed sourced. Why duplicate and add complexity?
- Django is realtively simple to deploy with Docker securely and scalably on any cloud service, keeping options flexible
- Django-ninja is FastAPI for Django, offering a fast way to serve models in a coupled or decoupled manner
- Move fast by starting off your project simple with django and decouple as and when you need. As you scale, your app in Django doesnt necessarily need to be rewritten

