# Generated by Django 5.0 on 2024-04-14 09:44

import django.core.serializers.json
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_flow_forge', '0009_flowbatch_flowbatchtempdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchHandler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_batches', models.IntegerField(default=0)),
                ('temp_data', models.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
                ('executed_flows', models.ManyToManyField(blank=True, related_name='batch_executed_flows', to='django_flow_forge.executedflow')),
                ('flow', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flowbatch_flow', to='django_flow_forge.flow')),
            ],
        ),
    ]