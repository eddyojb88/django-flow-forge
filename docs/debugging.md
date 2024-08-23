# Debugging

## Running selective tasks in a Pipeline
If you only want to run a small portion of the pipeline, you can comment out registered tasks of the flow.
When you go to run the flow, you can insert the ```ignore_task_dependencies``` keyword:

```run_flow('your_flow', ignore_task_deps_in_debug_mode=True, **kwargs)```

Warning: Be aware that this currently breaks the DAG in the visualisation tools as it doesn't yet handle missing dependencies.

<!-- ## Stepping through each Task stepwise and in sequence
In order to debug and run through each Task stepwise, you would need to set breakpoints at each function you care about, or you can copy and paste this:

```
class DebugExecutor:
    def debug_mode(self, executor, **kwargs):
        print(f'Running function {executor.task_name}')
        executor.task_output = executor.function(**kwargs)
        return
```

set a breakpoint at the ```executor.function(**kwargs)``` and then call a flow like this:

```run_flow('your_flow',  debug_executor=DebugExecutor(), **kwargs)``` -->