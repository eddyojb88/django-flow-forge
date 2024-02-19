def get_cytoscape_nodes_and_edges(tasks, show_nested=False):
    
    nodes = []
    edges = []

    def add_tasks_to_graph(tasks, target_task_id=None, assigning_bidirectional_edges=False):

        for task in tasks:

            if not show_nested and task.nested:
                pass

            else:
                # Ensure each task has a unique identifier; using task.id for uniqueness
                task_id = str(task.id)  # Convert to string to ensure compatibility with Cytoscape
                task_node = {'data': {'id': task_id, 'label': task.task_name}}
                if task_node not in nodes:
                    nodes.append(task_node)

                # If the task has a parent, add an edge indicating the dependency direction
                if target_task_id:
                    # nested_js_bool = str(task.nested).lower()  # Used to segregate nested nodes:
                    # if task.nested:
                        # print('here')
                    edge = {'data': {'source': task_id, 'target': target_task_id, 'nested': task.nested}}
                    if edge not in edges:
                        edges.append(edge)

                if not assigning_bidirectional_edges:
                    # Recursively add nested tasks' dependencies
                    parent_tasks = task.depends_on.all()
                    if parent_tasks.exists():
                        add_tasks_to_graph(tasks=parent_tasks, target_task_id=task_id)

                    tasks_depends_bidirectionally_with = task.depends_bidirectionally_with.all()
                    if tasks_depends_bidirectionally_with.exists():
                        add_tasks_to_graph(tasks=tasks_depends_bidirectionally_with, target_task_id=task_id, 
                                        assigning_bidirectional_edges=True
                                        )

    # Start adding tasks to the graph; no parent_id for top-level tasks
    add_tasks_to_graph(tasks)

    # Prepare and return the graph data structured for Cytoscape
    graph_json = {
        'nodes': nodes,
        'edges': edges
    }

    return graph_json