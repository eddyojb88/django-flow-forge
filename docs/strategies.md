# System Design Strategies

Given that there are infinite variations, this page documents some example strategies when using this module in case you are wondering whether it is an appropriate choice for your project.

## Long Running Flows

### Long running, high compute intensity:
If you are, for example, running a task once a day that is intensive for a period of time, you could run another replica of your django project and develop a small API that accepts a call to run the ```run_flow``` function. The API could be built in Django-Ninja.

You could also have a number of replicas behind a load balancer (e.g. Kubernetes)

### Long running, low compute intensity:
If it is a long running task but not that compute intensive, you could call the ```run_flow``` in async, or if calling with a view, use django-channels to offload the task out of the main loop and provide updates to a user in an app.

## Realtime Streaming Data
Consider Apache-Beam, either within a Task in the django-flow-forge framework or completely seperately.