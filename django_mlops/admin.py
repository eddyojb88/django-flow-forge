from django.contrib import admin
from . import models

@admin.register(models.Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('process_name',)
    search_fields = ['process_name']

@admin.register(models.ProcessTask)
class ProcessTaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'process', 'get_dependencies_display', 'get_bidirectional_dependencies_display', 'task_output')
    list_filter = ('process',)
    search_fields = ['task_name', 'process__process_name']
    filter_horizontal = ('depends_on', 'depends_bidirectionally_with')

    def get_dependencies_display(self, obj):
        """Return a string representation of the dependencies."""
        return ", ".join([dependency.task_name for dependency in obj.depends_on.all()])
    get_dependencies_display.short_description = 'Dependencies'

    def get_bidirectional_dependencies_display(self, obj):
        """Return a string representation of the bidirectional dependencies."""
        return ", ".join([dependency.task_name for dependency in obj.depends_bidirectionally_with.all()])
    get_bidirectional_dependencies_display.short_description = 'Bidirectional Dependencies'

@admin.register(models.ExecutedProcess)
class ExecutedProcessAdmin(admin.ModelAdmin):
    list_display = ('process', 'start_time', 'end_time', 'executed_by', 'process_complete')
    list_filter = ('process', 'process_complete')
    search_fields = ['process__process_name', 'executed_by']
    filter_horizontal = ('executed_tasks',)
    readonly_fields = ('process_snapshot',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            # process_snapshot is always read-only
            return self.readonly_fields + ('start_time', 'end_time', 'process', 'executed_tasks', 'executed_by', 'process_complete')
        return self.readonly_fields

@admin.register(models.ExecutedTask)
class ExecutedTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'process_run', 'start_time', 'end_time', 'task_complete')
    list_filter = ('process_run', 'task_complete')
    search_fields = ['task__task_name', 'process_run__process__process_name']
    readonly_fields = ('output', 'task_snapshot_id')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            # Making 'output' and 'task_snapshot_id' read-only for existing objects
            return self.readonly_fields + ('task', 'process_run', 'start_time', 'end_time', 'task_complete')
        return self.readonly_fields
