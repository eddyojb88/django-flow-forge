document.addEventListener('DOMContentLoaded', function() {
    var cy = cytoscape({
        container: document.getElementById('cy'),
        // other options...
    });

    // Use processData directly
    processData.forEach(function(process) {
        cy.add([
            { group: 'nodes', data: { id: process.task_name } }
        ]);
        process.dependencies.forEach(function(dependency) {
            cy.add([
                { group: 'edges', data: { source: dependency, target: process.task_name } }
            ]);
        });
    });

    cy.layout({
        name: 'dagre',
        padding: 10
    }).run();
});
