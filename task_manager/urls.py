"""task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks.views import *
from tasks.apiviews import *
from rest_framework_nested import routers
from django.urls import include
from django.contrib.auth.views import LogoutView

router = routers.SimpleRouter()
router.register("api/task", TaskViewSet)
tasks_router = routers.NestedSimpleRouter(router, 'api/task', )
tasks_router.register("history", TaskHistoryViewSet, basename='task-history')

urlpatterns = [
    path("", handle_home),
    path("all-tasks/", TaskListView.as_view()),
    path("pending-tasks/", PendingTaskListView.as_view()),
    path("completed-tasks/", CompletedTaskListView.as_view()),
    path("create-task/", TaskCreateView.as_view()),
    path('tasks/<pk>/update' , UpdateTaskView.as_view()),
    path('tasks/<pk>' , TaskDetailView.as_view()),
    path("tasks/<pk>/delete", DeleteTaskView.as_view()),
    path("user/signup", UserCreationView.as_view()),
    path("user/<pk>/update/", UserUpdationView.as_view()),
    path("user/<pk>/password/", PasswordUpdationView.as_view()),
    path("user/login", UserLoginView.as_view()),
    path("user/logout", LogoutView.as_view()),
    path("complete-task/<pk>", complete_task),
    path("admin/", admin.site.urls),
] + router.urls + tasks_router.urls
