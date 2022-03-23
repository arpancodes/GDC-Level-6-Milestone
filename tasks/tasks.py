from datetime import timedelta
from celery.decorators import periodic_task
from tasks.models import *
from django.core.mail import send_mail
import time
from datetime import datetime
from django.db.models.functions import TruncMinute

@periodic_task(run_every=timedelta(seconds=60))
def send_email_reminder():
    print("Starting to process Emails")
    for user in CustomUser.objects.annotate(preferred_minute=TruncMinute('preferred_email_time')).filter(preferred_minute=time.strftime("%H:%M")):
        pending_qs = Task.objects.filter(user=user, completed=False, deleted=False)
        email_content = f"""
        You have {pending_qs.count()} Pending Tasks
        ============================================
        Status      | Count
        ============================================
        PENDING     | {pending_qs.filter(status="PENDING").count()}
        IN_PROGRESS | {pending_qs.filter(status="IN_PROGRESS").count()}
        COMPLETED   | {pending_qs.filter(status="COMPLETED").count()}
        CANCELLED   | {pending_qs.filter(status="CANCELLED").count()}
        ============================================
        """
        send_mail("Pending Tasks from Tasks Manager", email_content, "tasks@task_manager.org", [user.email])
        print(f"Completed Processing User {user.id}")
