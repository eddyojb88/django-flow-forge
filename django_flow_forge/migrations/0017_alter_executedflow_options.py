# Generated by Django 5.0.7 on 2024-08-01 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_flow_forge', '0016_executedflow_flow_batch'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='executedflow',
            options={'ordering': ['-start_time']},
        ),
    ]
