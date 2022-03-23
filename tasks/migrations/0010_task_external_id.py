# Generated by Django 4.0.1 on 2022-03-23 01:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='external_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
    ]
