# Generated by Django 5.0.7 on 2024-08-20 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_flow_forge', '0019_remove_mlresult_metrics_mlresult_evaluation_metrics_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mlresult',
            name='feature_importances',
        ),
    ]
