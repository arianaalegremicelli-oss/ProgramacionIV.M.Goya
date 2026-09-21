from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


def health_version(request):
    return JsonResponse({"version": "0.1.0"})


@api_view(["GET"])
def project_list(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


# Tarea domiciliaria: Obtener un unico proyecto por su ID con get_object_or_404
@api_view(["GET"])
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    serializer = ProjectSerializer(project)
    return Response(serializer.data)


@api_view(["GET"])
def task_list(request):
    # Optimizamos las consultas para evitar el problema N+1
    tasks = Task.objects.select_related("project").prefetch_related("tags").all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)
