# Fragmento de taskflow/core/views.py  –  cambios de la Clase 6
# Alumna: Ariana Alegre Micelli

from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import IsAuthenticated

from .repositories import TaskRepository
from .serializers import ProjectSerializer, TaskSerializer
from .serializers_auth import RegisterSerializer
from .services import TaskService


class RegisterView(generics.CreateAPIView):
    queryset         = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class TaskViewSet(viewsets.ModelViewSet):
    queryset       = TaskRepository.get_queryset()
    serializer_class = TaskSerializer
    filterset_fields  = ["status", "priority", "project"]
    ordering_fields   = ["due_date", "created_at", "priority"]
    search_fields     = ["title", "description"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada usuario sólo ve sus propias tareas (owner)
        return super().get_queryset().filter(owner=self.request.user)

    def perform_create(self, serializer):
        # El propietario se asigna automáticamente; el cliente no lo envía
        serializer.save(owner=self.request.user)
