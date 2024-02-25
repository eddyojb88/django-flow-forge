from django.db import models

class Process(models.Model):

    process_name = models.CharField(null=False, blank=False, max_length=255, unique=True)  # Assuming each process name is unique
    process_display_name = models.CharField(null=True, blank=True, max_length=255,)
    in_current_code_base = models.BooleanField(default=True, null=False, blank=True)

    def save(self, *args, **kwargs):
        # Check if process_display_name is not provided or is empty
        if not self.process_display_name:
            # Replace underscores with spaces and capitalize each word
            self.process_display_name = self.process_name.replace('_', ' ').title()
        super(Process, self).save(*args, **kwargs)


    def __str__(self):
        return self.process_name

class ProcessTask(models.Model):

    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='tasks')  # Link to Process
    task_name = models.CharField(max_length=255)
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True)
    task_output = models.JSONField(default=dict)  # Field to store the function output
    depends_bidirectionally_with = models.ManyToManyField('self', symmetrical=True, blank=True, related_name='+')
    nested = models.BooleanField(default=False, null=False, blank=True)

    class Meta:
        unique_together = [['process', 'task_name']]  # Updated to reference 'process' instead of 'process_name'

    def __str__(self):
        return f"{self.process.process_name} - {self.task_name}"

class ExecutedProcess(models.Model):

    STATUS_CHOICES = (
        ('complete', 'Complete'),
        ('still_running', 'Still Running'),
        ('failed', 'Failed'),
        )

    process = models.ForeignKey(Process, null=True, on_delete=models.SET_NULL, related_name='process_runs')
    process_id_snapshot = models.BigIntegerField(null=True, blank=True,)
    process_name_snapshot = models.CharField(null=True, blank=True, max_length=255)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    executed_tasks = models.ManyToManyField(ProcessTask, related_name='executed_tasks', blank=True)
    executed_by = models.CharField(null=True, blank=True, max_length=255)
    process_complete = models.BooleanField(default=False)  # Indicates if the process run is complete
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='still_running')
    last_checkpoint_datetime = models.DateTimeField(blank=True, auto_now_add=True)
    process_snapshot = models.JSONField(default=dict)  # Captures the output of the task for this run

    def __str__(self):
        return f"Run of {self.process.process_name} on {self.start_time}. Completed: {self.process_complete}"

    def __str__(self):
        return f"Run of {self.process.process_name} on {self.start_time}. Completed: {self.process_complete}"

class ExecutedTask(models.Model):

    process_run = models.ForeignKey(ExecutedProcess, on_delete=models.CASCADE, related_name='task_runs')
    task = models.ForeignKey(ProcessTask, null=True, blank=True, on_delete=models.SET_NULL, related_name='runs')
    task_snapshot_id = models.BigIntegerField(null=True, blank=True,) # A snapshot of the task id at runtime so that graph viz can ref even if code and tasks change over time
    task_name_snapshot = models.CharField(null=True, blank=True, max_length=255)
    task_snapshot = models.JSONField(default=dict)  # Captures the task state at the time of this run
    output = models.JSONField(null=True, default=dict)  # Captures the output of the task for this run
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    task_complete = models.BooleanField(default=False)  # Indicates if the task run is complete


    def __str__(self):
        if not self.task:
            task_name = self.task_snapshot['task_name']
        else:
            task_name = self.task.task_name
        return f"Run of '{task_name}' for '{self.process_run}'. Completed: {self.task_complete}"
    
class MLResult(models.Model):

    executed_process = models.ForeignKey(ExecutedProcess, null=True, blank=True, on_delete=models.SET_NULL, related_name='ml_runs')
    experiment = models.CharField(null=True, blank=True, max_length=255)
    dataset = models.CharField(null=True, blank=True, max_length=255)
    algorithm = models.CharField(null=True, blank=True, max_length=255)
    parameters = models.JSONField(default=dict)  # Parameters used for this particular run
    metrics = models.JSONField(default=dict)  # Results/metrics from the experiment
    result_file_path = models.CharField(max_length=255, blank=True)  # Path to any result file
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)  # Any additional notes about the experiment

    def __str__(self):
        return f"{self.experiment} -  {self.algorithm} - {self.created_at.strftime('%Y-%m-%d')}"
