# Generated by Django 5.1.3 on 2024-12-07 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share_plans', '0002_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='time_to',
            field=models.TimeField(null=True),
        ),
    ]
