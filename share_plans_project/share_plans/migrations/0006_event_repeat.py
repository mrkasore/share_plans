# Generated by Django 5.1.3 on 2024-12-17 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share_plans', '0005_follower'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='repeat',
            field=models.BooleanField(default=False),
        ),
    ]
