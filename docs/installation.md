# Install via Pip

```pip install django_flow_forge```

However, if new to this module see the next section

# Quickstart
It is recommended to clone the repo in order to view the ```example_project``` in action.

Quickest route to this if you have Docker installed is:

```docker compose -f docker-compose-local.yml up```

Pip:

Once the repo has been cloned, you can either install the requirements in your virtual env (virtualenv, conda etc). e.g.

```pip install -r requirements.txt```

However, if you are interested in viewing how tasks in async are run in the ```pipeline_simple_with_celery.py``` example, you will also need a task server running, such as RabbitMQ or Redis. The recommended way to view this simply is to use the docker-compose file in the step above.