from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from tasks.models import Task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView




def session_storage_view(request):
		total_views = request.session.get('total_views', 0)
		request.session['total_views'] = total_views + 1
		return HttpResponse(f"Total Views is {total_views}")

class AuthorisationCheck(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)

class CustomAuthenticationForm(AuthenticationForm):
		def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.fields['username'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'
				self.fields['password'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'


class UserLoginView(LoginView):
		form_class = CustomAuthenticationForm
		template_name = "user_login.html"

class CustomUserCreationForm(UserCreationForm):
		def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.fields['username'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'
				self.fields['password1'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'
				self.fields['password2'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'

class UserCreationView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"


class TaskListView(LoginRequiredMixin, ListView):
		queryset = Task.objects.filter(deleted=False).order_by("priority")
		paginate_by = 5
		context_object_name = 'tasks'
		template_name = 'tasks_all.html'

		def get_queryset(self):
				return self.queryset.filter(user=self.request.user)

		def get_context_data(self, **kwargs):
				context = super(TaskListView, self).get_context_data(**kwargs)
				context.update({'total_completed': self.get_queryset().filter(completed=True).count(), "total_tasks": self.get_queryset().count()})
				return context

class PendingTaskListView(LoginRequiredMixin, ListView):
		paginate_by = 5
		context_object_name = 'tasks'
		template_name = 'tasks_pending.html'

		def get_queryset(self):
				tasks = Task.objects.filter(deleted=False, user=self.request.user).filter(completed=False).order_by("priority")
				return tasks

		def get_context_data(self, **kwargs):
				context = super(PendingTaskListView, self).get_context_data(**kwargs)
				context.update({'total_pending': self.get_queryset().count()})
				return context



class CompletedTaskListView(LoginRequiredMixin, ListView):
		paginate_by = 5
		context_object_name = 'tasks'
		template_name = 'tasks_completed.html'

		def get_queryset(self):
				tasks = Task.objects.filter(deleted=False, user=self.request.user).filter(completed=True).order_by("priority")
				return tasks
		def get_context_data(self, **kwargs):
				context = super(CompletedTaskListView, self).get_context_data(**kwargs)
				context.update({'total_completed': self.get_queryset().count()})
				return context

class TaskCreateForm(ModelForm):

		def clean_title(self):
				title = self.cleaned_data["title"]
				if(len(title) < 10):
						raise ValidationError("The value must be atleast 10 charecters")
				return title

		class Meta:
				model = Task
				fields = ["title","description", "priority"]

		def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.fields['title'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'
				self.fields['description'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'
				self.fields['priority'].widget.attrs['class'] = 'bg-gray-200 w-full py-2 px-3 rounded-lg text-gray-700 focus:outline-none focus:shadow-outline'

def validate_priority(task):
    """Cascase validation for priority"""
    tasks = Task.objects.filter(deleted=False, user=task.user, completed=False).exclude(pk=task.pk)
    priority = task.priority
    updated_tasks = []
    while task := tasks.filter(priority=priority).first():
        priority += 1
        task.priority = priority
        updated_tasks.append(task)
    Task.objects.bulk_update(updated_tasks, ["priority"])

class TaskCreateView(CreateView):
		form_class=TaskCreateForm
		template_name = "task_create.html"
		success_url = '/'

		def form_valid(self, form):
				"""If the form is valid, save the associated model."""
				print(form)
				self.object = form.save()
				self.object.user = self.request.user
				self.object.save()
				validate_priority(self.object)
				return HttpResponseRedirect(self.success_url)

		def get_context_data(self, **kwargs):
				context = super(TaskCreateView, self).get_context_data(**kwargs)
				context.update({'title': "Create Task"})
				return context

class UpdateTaskView(AuthorisationCheck, UpdateView):
		model=Task
		form_class = TaskCreateForm
		template_name = "task_create.html"
		success_url = '/'


		def form_valid(self, form):
				"""If the form is valid, save the associated model."""
				self.object = form.save()
				validate_priority(self.object)
				return HttpResponseRedirect(self.success_url)

		def get_context_data(self, **kwargs):
				context = super(UpdateTaskView, self).get_context_data(**kwargs)
				context.update({'title': "Update Task"})
				return context

class TaskDetailView(AuthorisationCheck, DetailView):
    model = Task
    template_name = "task_detail.html"

class DeleteTaskView(AuthorisationCheck, DeleteView):
    success_url = "/"
    model = Task
    template_name = "task_delete.html"

def complete_task(request, pk):
    task = Task.objects.get(pk=pk)
    task.completed = True
    task.save()
    return HttpResponseRedirect("/completed-tasks/")

def handle_home(request):
    return HttpResponseRedirect("/all-tasks/")
