from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

class Flow(models.Model):

    flow_name = models.CharField(null=False, blank=False, max_length=255, unique=True)  # Assuming each flow name is unique
    flow_display_name = models.CharField(null=True, blank=True, max_length=255,)
    in_current_code_base = models.BooleanField(default=True, null=False, blank=True)

    class Meta:
        permissions = [
            ("django_flow_admin_access", "Can access Django Flow Admin"),
        ]


    def save(self, *args, **kwargs):
        # Check if flow_display_name is not provided or is empty
        if not self.flow_display_name:
            # Replace underscores with spaces and capitalize each word
            self.flow_display_name = self.flow_name.replace('_', ' ').title()
        super(Flow, self).save(*args, **kwargs)


    def __str__(self):
        return self.flow_name

class FlowTask(models.Model):

    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name='tasks')  # Link to Flow
    task_name = models.CharField(max_length=255)
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True)
    task_output = models.JSONField(default=dict)  # Field to store the function output
    depends_bidirectionally_with = models.ManyToManyField('self', symmetrical=True, blank=True,)
    nested = models.BooleanField(default=False, null=False, blank=True)
    docstring = models.TextField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = [['flow', 'task_name']]  # Updated to reference 'flow' instead of 'flow_name'

    def __str__(self):
        return f"{self.flow.flow_name} - {self.task_name}"

STATUS_CHOICES = (
    ('complete', 'Complete'),
    ('pending', 'Pending'),
    ('failed', 'Failed'),
    ('in_progress', 'In Progress'),
    )
    
class ExecutedFlow(models.Model):

    flow = models.ForeignKey(Flow, null=True, on_delete=models.SET_NULL, related_name='flow_runs')
    flow_id_snapshot = models.BigIntegerField(null=True, blank=True,)
    flow_name_snapshot = models.CharField(null=True, blank=True, max_length=255)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    batch_handler = models.ForeignKey('BatchHandler', on_delete=models.CASCADE, related_name='executed_flows', null=True, blank=True)
    flow_batch = models.ForeignKey('FlowBatch', on_delete=models.CASCADE, related_name='executed_flows', null=True, blank=True)  # Added field
    # executed_tasks = models.ManyToManyField(FlowTask, related_name='executed_tasks', blank=True)
    executed_by = models.CharField(null=True, blank=True, max_length=255)
    flow_complete = models.BooleanField(default=False)  # Indicates if the flow run is complete
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_checkpoint_datetime = models.DateTimeField(blank=True, auto_now_add=True)
    flow_snapshot = models.JSONField(default=dict)  # Captures the output of the task for this run
    exceptions = models.JSONField(default=dict, null=True, blank=True)
    params = models.JSONField(default=dict, null=True, blank=True)
    meta = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        if self.flow:
            return f"Run of {self.flow.flow_name} on {self.start_time}. Completed: {self.flow_complete}"
        else:
            return f"Run of an unknown flow on {self.start_time}. Completed: {self.flow_complete}"

class ExecutedTask(models.Model):

    flow_run = models.ForeignKey(ExecutedFlow, on_delete=models.CASCADE, related_name='task_runs')
    task = models.ForeignKey(FlowTask, null=True, blank=True, on_delete=models.SET_NULL, related_name='runs')
    task_snapshot_id = models.BigIntegerField(null=True, blank=True,) # A snapshot of the task id at runtime so that graph viz can ref even if code and tasks change over time
    task_name_snapshot = models.CharField(null=True, blank=True, max_length=255)
    task_snapshot = models.JSONField(default=dict)  # Captures the task state at the time of this run
    output = models.JSONField(null=True, default=dict)  # Captures the output of the task for this run
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    task_complete = models.BooleanField(default=False)  # Indicates if the task run is complete
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    exceptions = models.JSONField(default=dict, null=True, blank=True,)

    def __str__(self):
        if not self.task:
            task_name = self.task_snapshot['task_name']
        else:
            task_name = self.task.task_name
        return f"Run of '{task_name}' for '{self.flow_run}'. Completed: {self.task_complete}"

class BatchHandler(models.Model):
    '''Model to handle batch processing using the same Flow - sometimes you want to run the flow in batches not batches within a flow.
       This is also a useful option if you want to chain together Flows in a batch'''
    batch_ref_name = models.CharField(null=True, blank=True, max_length=255) # Optional reference name
    total_batch_count = models.IntegerField(default=0, null=False, blank=False,)
    temp_data = models.JSONField(null=True, default=dict, encoder=DjangoJSONEncoder)
    date_initialised = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.batch_ref_name} (Batch count: {self.total_batch_count})'

class FlowBatch(models.Model):
    batch_handler = models.ForeignKey(BatchHandler, on_delete=models.CASCADE, related_name='batch', null=True, blank=True)
    flow_batch_number = models.IntegerField(default=0, null=False, blank=False,)
    # executed_flows = models.ForeignK
    temp_data = models.JSONField(null=True, default=dict, encoder=DjangoJSONEncoder)

class MLResult(models.Model):

    executed_flow = models.ForeignKey(ExecutedFlow, null=True, blank=True, on_delete=models.SET_NULL, related_name='ml_runs')
    experiment = models.CharField(null=True, blank=True, max_length=255)
    dataset = models.CharField(null=True, blank=True, max_length=255)
    algorithm = models.CharField(null=True, blank=True, max_length=255)
    parameters = models.JSONField(default=dict)  # Parameters used for this particular run
    metrics = models.JSONField(default=dict)  # Results/metrics from the experiment
    result_file_path = models.CharField(max_length=255, blank=True)  # Path to any result file
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)  # Any additional notes about the experiment

    def __str__(self):
        return f"{self.algorithm} - Experiment Desc.:{self.experiment} - {self.created_at.strftime('%Y-%m-%d')}"
