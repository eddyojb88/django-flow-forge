# Generated by Django 5.0 on 2024-04-14 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_flow_forge', '0011_remove_flowbatchtempdata_batch_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batchhandler',
            old_name='total_batches',
            new_name='total_batch_count',
        ),
    ]
