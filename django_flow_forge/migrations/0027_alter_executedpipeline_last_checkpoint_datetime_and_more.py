# Generated by Django 5.1 on 2024-10-09 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_flow_forge', '0026_executedtask_last_checkpoint_datetime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='executedpipeline',
            name='last_checkpoint_datetime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='executedtask',
            name='last_checkpoint_datetime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
