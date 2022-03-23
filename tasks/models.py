
from django.db import models
from uuid import uuid4

from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)

class Task(models.Model):
    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    user = models.ForeignKey(User , on_delete=models.CASCADE , null=True,blank=True)
    priority = models.IntegerField()

    def __str__(self):
        return self.title

class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    prev_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task.title + " - " + self.prev_status + " to " + self.new_status


@receiver(pre_save, sender=Task)
def signal_product_manage_latest_version_id(sender, instance, update_fields=None, **kwargs):
    try:
        old_instance = Task.objects.get(id=instance.id)
    except Task.DoesNotExist:  # to handle initial object creation
        return None # no need to do anything

    if old_instance.status != instance.status:
        TaskHistory.objects.create(task=instance, prev_status=old_instance.status, new_status=instance.status)
