from .models import *
from django.test import TestCase, RequestFactory
from .views import *

class QuestionModelTests(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman")


    def test_protected_route(self):
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
