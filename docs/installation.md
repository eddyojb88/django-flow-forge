# Installation

##    Install via Pip

```pip install django-flow-forge```

However, if new to this module see the next section for an example app.


If not, then remember to add
```django_flow_forge``` to your list of ```INSTALLED_APPS``` in ```settings.py``` and
```path('django_flow_forge/', include('django_flow_forge.urls')),``` to ```urls.py```.

## Quickstart Example Project
It is recommended to clone the repo in order to view the ```example_project``` in action.

### Docker

Once cloned, the quickest route to viewing if you have Docker installed is:

```docker compose -f docker-compose-local.yml up```

Then log in to the django container

### Pip:

Once the repo has been cloned, you can either install the requirements in your virtual env (virtualenv, conda etc). e.g.

```pip install -r requirements.txt```

However, if you are interested in viewing how tasks in async are run in the ```pipeline_simple_with_celery.py``` example, you will also need a task server running, such as RabbitMQ or Redis. The recommended way to view this simply is to use the docker-compose file in the step above.

### Applying Migration to Database

The database is a sqlite file with code in the example project to modify it so that it can allow celery to interact with it.
N.B. a production solution is a database like Postgres or warehouse like Snowflake.

Go in to the ```example_project``` directory and migrate the DB:

```python manage.py migrate```

### Enable registering of flows
Now that the database has a recognition of Flows and Tasks, go in to ```views.py``` within the ```example_app``` and uncomment the 
line ```# from . import pipeline_simple, pipeline_with_nested_tasks...```

Optional: If you also want to run the celery example, also uncomment the following:

```from . import  pipeline_simple_with_celery```

This allows these scripts to be included as part of the project scope. At the bottom of these scripts are flow definitions, which are registered register_pipelines()

N.B. Pipeline is taken to mean the same as a 'Flow'.  However, pipelines sound rigid, which this module isn't supposed to be. The disctinction isn't actually clear - A decade ago they were always called flows.

### Start Celery Worker (Optional):

In a new terminal window:

```cd example_project```

```celery -A example_app  worker --loglevel=info```

## Run the server and start tasks

```python manage.py runserver 0.0.0.0:8000```

Now go to:

```http://localhost:8005/example/```

You will see a list of tasks. You can click on each of them one at a time. Unfortunately, the page isn't yet async so when you run it, you will get a message saying 'Task executed successfully' but then you have to refresh the page to run another.

Continue clicking each example. The ML grid search example will take a minute

Warning: if you have celery worker running, at the moment the celery example will stall.

## View the results in a dashboard:

```http://localhost:8005/django_flow_forge/task-runs-viz/```

If wanting to conceptualize a task for stakeholders before or during development, you can view the pipeline in concept by going to:

```
http://localhost:8005/django-flow-forge/conceptual-dag-viz/

<img width="1057" alt="Screenshot 2024-02-27 at 11 45 02" src="https://github.com/eddyojb88/django-flow-forge/assets/22086433/36e80d55-4968-40e1-bf73-9eaef5247a8f">

More details on this can be found in Dashboard section


## Running tasks with no web server
A great feature of this module is that you can develop and run tasks without the web server.
See the  ``run_tasks_no_server.py``` script to see how this works.