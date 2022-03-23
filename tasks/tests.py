from .models import *
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory
from .views import *
from .apiviews import *
import time
from django.core import mail
from .tasks import send_email_reminder
from rest_framework.test import force_authenticate


class QuestionModelTests(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.api_factory = APIRequestFactory()
        self.user = CustomUser.objects.create_user(username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman", first_name="Bruce", last_name="Wayne", preferred_email_time=time.strftime("%H:%M"))


    def test_unauthenticated(self):
            """
            Try to GET the tasks listing page, expect the response to redirect to the login page
            """
            response = self.client.get("/all-tasks/")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/user/login?next=/all-tasks/")

    def test_authenticated(self):
            # Create an instance of a GET request.
            request = self.factory.get("/all-tasks/")
            # Set the user instance on the request.
            request.user = self.user
            # We simply create the view and call it like a regular function
            response = TaskListView.as_view()(request)
            # Since we are authenticated we get a 200 response
            self.assertEqual(response.status_code, 200)

    def test_task_create_invalid_title(self):
        """
        Test the task create view with an invalid title (less than 10 characters)
        """
        request = self.factory.post("/all-tasks/", {"title": "Test Task", "description": "Test Description", "priority": 1, "status": "PENDING"})
        request.user = self.user
        response = TaskCreateView.as_view()(request)
        content = response.render().content.decode('utf8')
        self.assertEqual("The value must be atleast 10 charecters" in content, True)
        self.assertEqual(Task.objects.filter(title="Test Task").count(), 0)

    def test_task_create(self):
        """
        Test the task create view
        """
        request = self.factory.post("/all-tasks/", {"title": "Test Task with more than 10 characters", "description": "Test Description", "priority": 1, "status": "PENDING"})
        request.user = self.user
        response = TaskCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertEqual(Task.objects.filter(title="Test Task with more than 10 characters").count(), 1)

    def test_task_list_api(self):
        """
        Test the tasks list api
        """
        request = self.api_factory.get("/api/tasks")
        request.user = self.user
        response = TaskViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)

    def test_task_detail_api(self):
        """
        Test the task detail api
        """
        task = Task.objects.create(title="Test Task", description="Test Description", priority=1, user=self.user)
        request = self.api_factory.get(f"/api/tasks/{task.external_id}")
        force_authenticate(request, user=self.user)
        response = TaskViewSet.as_view({'get': 'retrieve'})(request, external_id=task.external_id)
        self.assertEqual(response.status_code, 200)

    def test_task_create_api(self):
        """
        Test the task create api
        """
        request = self.api_factory.post("/api/tasks", {"title": "Test Task", "description": "Test Description", "priority": 1})
        force_authenticate(request, user=self.user)
        response = TaskViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)

    def test_task_status_change_api(self):
        """
        Test the task status change api
        """
        task = Task.objects.create(title="Test Task", description="Test Description", priority=1, user=self.user)
        request = self.api_factory.patch(f"/api/tasks/{task.external_id}", {"status": "COMPLETED"})
        force_authenticate(request, user=self.user)
        response = TaskViewSet.as_view({'patch': 'partial_update'})(request, external_id=task.external_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TaskHistory.objects.filter(task=task).count(), 1)

    def test_report_mail(self):
        """
        Test the report mail function
        """
        send_email_reminder()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Pending Tasks from Tasks Manager")
