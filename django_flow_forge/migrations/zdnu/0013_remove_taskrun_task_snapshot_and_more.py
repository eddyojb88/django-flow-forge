# Generated by Django 5.0.2 on 2024-02-19 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_flow_forge', '0012_process_process_display_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskrun',
            name='task_snapshot',
        ),
        migrations.AddField(
            model_name='processrun',
            name='process_snapshot',
            field=models.JSONField(default=dict),
        ),
    ]
