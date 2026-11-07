# taskflow/core/views.py
# Alumna: Ariana Alegre Micelli

from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Tag
from .repositories import TaskRepository
from .serializers import ProjectSerializer, TagSerializer, TaskSerializer
from .services import ProjectService, TaskService


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        """GET /api/projects/<id>/summary/"""
        project = self.get_object()
        data = ProjectService.project_summary(project)
        return Response(data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = TaskRepository.get_queryset()
    serializer_class = TaskSerializer

    filterset_fields = ["status", "priority", "project"]
    ordering_fields = ["due_date", "created_at", "priority"]
    search_fields = ["title", "description"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """POST /api/tasks/<id>/complete/"""
        task = self.get_object()
        TaskService.mark_completed(task)
        return Response(self.get_serializer(task).data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """GET /api/tasks/overdue/"""
        tasks = TaskService.tasks_overdue(self.get_queryset())
        page = self.paginate_queryset(tasks)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(tasks, many=True).data)
