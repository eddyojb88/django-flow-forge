# Generated by Django 5.0.2 on 2024-02-14 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('process_name', models.CharField(max_length=255)),
                ('task_name', models.CharField(max_length=255)),
                ('dependencies', models.ManyToManyField(blank=True, to='django_flow_forge.processtask')),
            ],
            options={
                'unique_together': {('process_name', 'task_name')},
            },
        ),
    ]
