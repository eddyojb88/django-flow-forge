# Debugging

## Running selective tasks in a Flow / Pipeline
If you only want to run a small portion of the pipeline, you can comment out registered tasks of the flow.
When you go to run the flow, you can insert the ```ignore_task_dependencies``` keyword:

```run_flow('your_flow', ignore_task_dependencies=True, **kwargs)```

## Stepping through each Task stepwise and in sequence
At the moment, in order to debug and run through each Task stepwise, you would need to set breakpoints at each function you care about.

Note:
What is on the roadmap and coming soon is to set a debug mode that allows you to set a breakpoint at the beginning / entry point of each Task function.