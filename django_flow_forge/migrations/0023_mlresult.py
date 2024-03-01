# Generated by Django 5.0.2 on 2024-02-23 21:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_mlops', '0022_executedprocess_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='MLResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experiment', models.CharField(blank=True, max_length=255, null=True)),
                ('dataset', models.CharField(blank=True, max_length=255, null=True)),
                ('algorithm', models.CharField(blank=True, max_length=255, null=True)),
                ('parameters', models.JSONField(default=dict)),
                ('metrics', models.JSONField(default=dict)),
                ('result_file_path', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('executed_process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='runs', to='django_mlops.executedprocess')),
            ],
        ),
    ]