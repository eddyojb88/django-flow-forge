# Generated by Django 5.0.2 on 2024-02-17 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_mlops', '0003_process_alter_processtask_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='processtask',
            name='nested_task',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]