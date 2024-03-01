# django-flow-forge

Django Flow Forge aims to simplify your Data Ops or ML system, steering clear of the unnecessary complexities of other packages and vendor lock-in that plague many projects.

Designed for Data Scientists and Data Engineers, this Django plugin module streamlines your tech stack, focusing on simplicity, flexibility, and impact.

![mlops_gif](https://github.com/eddyojb88/django-flow-forge/assets/22086433/9ea13500-2019-4145-995f-1fd855f51c74)

# Motivation

[Read the Docs](https://eddyojb88.github.io/django-flow-forge/) for more info on this

# Features

- Easily define your flows / pipeline processes as a DAG
- Visualize your flows for stakeholders, both in planning and development phases (inspired by Kedro)
- Simple pipeline registration and execution through a script, Django website or via an API by plugging in Django-ninja (Fast API for Django))
- Task monitoring and visualization of outputs and failures.
- Visualise pipeline process outputs and failures for each task (inspired by Kedro)
- Compare data science experiment results easily
- Serve your models by plugging in Django Ninja
- A familiar environment for Django users, minimizing the learning curve
- Leverage Django's robust security
- Leverage Django's existing scalability features, including Django Celery and flexbility with Kubernetes engines, without the worry of vendor lock-in
- Encourages teams to move away from Notebooks, which cause a plethora of issues

 ## Features to come
 - Documentation page
 - Implement better authentication and authorization options (at the moment you have to import the views in to urls and add login_required
 - Async capability: allow user to use the dependency tree in the graph in order to wait for relevant tasks that have been offloaded to complete
 - Make stakeholder only facing dashboard to display only tasks that succeeded

# Quick Start

Docs are here: [Read the Docs](https://eddyojb88.github.io/django-flow-forge/).

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
http://localhost:8005/django-flow-forge/task-runs-viz/
```

If wanting to conceptualize a task for stakeholders before or during development, you can view the pipeline in concept by going to:

```
http://localhost:8005/django-flow-forge/conceptual-dag-viz/

<img width="1057" alt="Screenshot 2024-02-27 at 11 45 02" src="https://github.com/eddyojb88/django-flow-forge/assets/22086433/36e80d55-4968-40e1-bf73-9eaef5247a8f">