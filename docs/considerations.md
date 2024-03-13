# Considerations

## What are Flows?

Flows in Django Flow Forge are database backed sequences of tasks designed to help automate data operations and machine learning operational workflows. Each Flow consists of multiple Tasks that can be executed in a specified order.
Tasks can contain logic that can be run in e.g. Celery or upscaled in Kuberenetes. 
Flows are designed to simplify complex data processing, machine learning model training, evaluation, and deployment processes by encapsulating them into manageable, repeatable, and scalable operations.

## How are Flows defined?

```    register_task_pipeline(
        flow_name='pipeline_simple_ml', 
        clear_existing_flow_in_db=True,
        pipeline = {
                    'fetch_data2': {'function': fetch_data2, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1', 'fetch_data2']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model, 'depends_on': ['analyze_data']},
                   }
    )
```
A flow is defined by registering a series of tasks, where each task is associated with a specific function to execute. Additional metadata describing its dependencies on other tasks is also defined in order to understand the task order. 
The flow's tasks are stored and managed in the database, enabling dynamic modification and scalable execution and tracking.

WARNING: It is important to set the 'depends_on' properly when parrelising tasks. If you don't set dependencies then the system will think they are all fine to run at the same time.

Also, when writing your Tasks, a good habit is to make sure they all have functional independence i.e. don't return large objects, especially not Pandas DataFrames, which aren't JSON serializable so should only be used within the function. Store your files to your system or even better database.

## Nested tasks

It's crucial to recognize that, as of the current implementation, nested tasks in Django-Flow-Forge are utilized primarily for visualization purposes. This means that while nested tasks significantly aid in depicting the structure and dependencies of a workflow in a more intuitive and detailed manner, they do not alter the execution logic of the pipeline. The primary execution flow treats these nested tasks as part of the linear sequence of tasks, irrespective of their hierarchical representation in the visualization.

## Visualising your flows in concept

<img width="1057" alt="Screenshot 2024-02-27 at 11 45 02" src="https://github.com/eddyojb88/django-flow-forge/assets/22086433/36e80d55-4968-40e1-bf73-9eaef5247a8f">

When running the server, you can go here in order to view your flows in concept:
```http://localhost:8005/django_flow_forge/conceptual-dag-viz/```

This is great for communicating to stakeholders what it is that you are working on.


## Scheduled Tasks

It is recommended to consider Celery Beat with Django for this. There is lots of documentation on this and the beauty of this module is that your choice of solution is not necessarily prescribed.

## Parallelisation
This is always a tricky topic and so care is required in designing from the outset.

This module was developed so that it can be flexible. Each Task in a Flow can be executed in parralel with others, so long as its dependencies have been met. 

To run a Task in Celery, this requires setting e.g. a @shared_task decorator to the specific functions that you want run in async and setting use_celery=True in the flow args (see example_project).

You can also run jobs in parallel within a Task (see pipeline_simple_celery example in example_project)

### Parallelisation within Parallelisation
What is very tricky is running distributed tasks within distributed tasks. It can be done but not advised. If you really want to go down this route, you can use the ```allow_join_result``` option in Celery to achieve this.