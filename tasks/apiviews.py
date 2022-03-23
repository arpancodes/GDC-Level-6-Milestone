from cgitb import lookup
from rest_framework.views import APIView
from rest_framework.serializers import ModelSerializer, UUIDField
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from tasks.models import Task, TaskHistory, User, STATUS_CHOICES
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend,FilterSet,CharFilter, ChoiceFilter, BooleanFilter, DateTimeFilter

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]

class TaskSerializer(ModelSerializer):
		user = UserSerializer(read_only=True)
		id = UUIDField(source="external_id", read_only=True)
		class Meta:
				model = Task
				fields = ["title", "description", "priority", "user", "status", "id", "completed"]

class TaskFilter(FilterSet):
		title = CharFilter(lookup_expr="icontains")
		status = ChoiceFilter(choices=STATUS_CHOICES)
		completed = BooleanFilter()

class TaskViewSet(ModelViewSet):
		queryset = Task.objects.all()
		serializer_class = TaskSerializer

		permission_classes = (IsAuthenticated,)

		filter_backends = (DjangoFilterBackend,)
		filterset_class = TaskFilter
		lookup_field = "external_id"

		def get_queryset(self):
				return Task.objects.filter(user=self.request.user)

		def perform_create(self, serializer):
				serializer.save(user=self.request.user)


class TaskHistoryFilter(FilterSet):
		prev_status = ChoiceFilter(choices=STATUS_CHOICES)
		new_status = ChoiceFilter(choices=STATUS_CHOICES)
		updated_date = DateTimeFilter()

class TaskHistorySerializer(ModelSerializer):
		task = TaskSerializer(read_only=True)
		class Meta:
				model = TaskHistory
				fields = ["task", "prev_status", "new_status", "updated_date"]

class TaskHistoryViewSet(ReadOnlyModelViewSet):
	serializer_class = TaskHistorySerializer

	permission_classes = (IsAuthenticated,)

	filter_backends = (DjangoFilterBackend,)
	filterset_class = TaskHistoryFilter
	def get_queryset(self):
			return TaskHistory.objects.filter(task__external_id=self.kwargs["nested_1_external_id"], task__user=self.request.user)


class ViewTasksAPIView(APIView):
    def get(self, request):
        tasks = Task.objects.filter(deleted=False)
        data = TaskSerializer(tasks, many=True).data
        return Response({"tasks": data})
