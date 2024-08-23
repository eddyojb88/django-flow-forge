# Installation

If you are not new to this project, you can install via ```pip install django-flow-forge```

## Quickstart Example Project
It is recommended to clone the Github repo in order to view the ```example_project``` in action.

### Docker

Once cloned, the quickest route to viewing if you have Docker installed is:

```docker compose -f docker-compose-local.yml up```

Then connect in to the django container

### Pip:

Once the repo has been cloned, you can either install the requirements in your virtual env (virtualenv, conda etc). e.g.

```pip install -r requirements.txt```

However, if you are interested in viewing how tasks in async are run in the ```pipeline_simple_with_celery.py``` example, you will also need a task server running, such as RabbitMQ or Redis. The recommended way to view this simply is to use the docker-compose file in the step above.

### Applying Migration to Database

The database is a sqlite file with code in the example project to modify it so that it can allow celery to interact with it.
N.B. a production solution is a database like Postgres or warehouse like Snowflake.

Go in to the ```example_project``` directory and migrate the DB:

```python manage.py migrate```

Also make sure to create a superuser to view the django flow forge pages since they are protected behind authentication:

```python manage.py createsuperuser```

### Enable registering of flows

Each pipeline has to be imported in some way. These are currently in ```example_project.example_app.pipelines```

## Run the server and start tasks

```python manage.py runserver 0.0.0.0:8000```

Now go to:

```http://localhost:8005/example/```

You will see a list of tasks. You can click on each of them one at a time. Unfortunately, the page isn't async so when you run it, you will need to wait before receiving a message saying that the 'Task executed successfully'.

Continue clicking each example. The ML grid search example will take a minute


### If using Celery (Optional):

If you want to see the examples in async, in a new terminal window:

```cd example_project```

```celery -A example_app  worker --loglevel=info```

## View the results in a dashboard:

You will need to be logged in first. Login via ```http://localhost:8005/admin```

Now go to:

```http://localhost:8005/django_flow_forge/task-runs-viz/```

If wanting to conceptualize a task for stakeholders before or during development, you can view the pipeline in concept by going to:

```
http://localhost:8005/django-flow-forge/conceptual-dag-viz/```

<img width="1057" alt="Screenshot 2024-02-27 at 11 45 02" src="https://github.com/eddyojb88/django-flow-forge/assets/22086433/36e80d55-4968-40e1-bf73-9eaef5247a8f">

More details on this can be found in Dashboard section


## Running tasks with no web server
A great feature of this module is that you can develop and run tasks without the web server.
See the  ```run_tasks_no_server.py``` script to see how this works.