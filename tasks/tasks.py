from datetime import timedelta
from celery.decorators import periodic_task
from tasks.models import *
from django.core.mail import send_mail
import time
from task_manager.celery import app

@periodic_task(run_every=timedelta(seconds=10))
def send_email_reminder():
    print("Starting to process Emails")
    for user in User.objects.all():
        pending_qs = Task.objects.filter(user=user, completed=False, deleted=False)
        email_content = f"You have {pending_qs.count()} Pending Tasks"
        send_mail("Pending Tasks from Tasks Manager", email_content, "tasks@task_manager.org", [user.email])
        print(f"Completed Processing User {user.id}")


@app.task
def test_background_jobs():
    print("This is from the bg")
    for i in range(10):
        time.sleep(1)
        print(i)
