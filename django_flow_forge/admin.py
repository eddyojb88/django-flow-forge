from django.contrib import admin
from django.utils.text import Truncator

from . import models

@admin.register(models.Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('pipeline_name',)
    search_fields = ['pipeline_name']

@admin.register(models.PipelineTask)
class PipelineTaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'pipeline', 'get_dependencies_display', 'task_output')
    list_filter = ('pipeline',)
    search_fields = ['task_name', 'pipeline__pipeline_name']
    # filter_horizontal = ('depends_on', 'depends_bidirectionally_with')

    def get_dependencies_display(self, obj):
        """Return a string representation of the dependencies."""
        return ", ".join([dependency.task_name for dependency in obj.depends_on.all()])
    get_dependencies_display.short_description = 'Dependencies'

@admin.register(models.ExecutedPipeline)
class ExecutedPipelineAdmin(admin.ModelAdmin):
    list_display = ('pipeline', 'pipeline_name_snapshot', 'start_time', 'end_time', 'executed_by', 'pipeline_complete')
    list_filter = ('pipeline', 'pipeline_complete')
    search_fields = ['pipeline__pipeline_name', 'executed_by']
    # filter_horizontal = ('executed_tasks',)
    readonly_fields = ('pipeline_snapshot',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            # pipeline_snapshot is always read-only
            return self.readonly_fields + ('start_time', 'end_time', 'pipeline', 'executed_tasks', 'executed_by', 'pipeline_complete')
        return self.readonly_fields

@admin.register(models.ExecutedTask)
class ExecutedTaskAdmin(admin.ModelAdmin):
    list_display = ('task_name_snapshot', 'pipeline_run', 'task', 'start_time', 'end_time', 'task_complete')
    list_filter = ('pipeline_run', 'task_complete')
    search_fields = ['task__task_name', 'pipeline_run__pipeline__pipeline_name']
    readonly_fields = ('output', 'task_snapshot_id')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            # Making 'output' and 'task_snapshot_id' read-only for existing objects
            return self.readonly_fields + ('task', 'pipeline_run', 
                                        #    'start_time', 'end_time',
                                             'task_complete')
        return self.readonly_fields

@admin.register(models.BatchHandler)
class BatchHandlerAdmin(admin.ModelAdmin):
    list_filter = ('batch_ref_name', 'date_initialised',)
    search_fields = ['task__task_name', 'date_initialised', 'pipeline_run__pipeline__pipeline_name']
    list_display = ('id', 'date_initialised', 'batch_ref_name', 'total_batch_count', 'temp_data',)

@admin.register(models.PipelineBatch)
class PipelineBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_date_initialised', 'batch_handler', 'pipeline_batch_number', 'truncated_temp_data',)

    def get_date_initialised(self, obj):
        return obj.batch_handler.date_initialised
    get_date_initialised.admin_order_field = 'batch_handler__date_initialised'  # Allows column order sorting
    get_date_initialised.short_description = 'Date Initialised'  # Renames the column header

    def truncated_temp_data(self, obj):
        return Truncator(obj.temp_data).chars(50)
    truncated_temp_data.short_description = 'Temp Data'  # Custom header for the truncated field