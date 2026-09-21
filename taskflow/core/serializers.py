from rest_framework import serializers
from .models import Project, Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    # Anidamos los tags para que se muestren con su nombre y no solo el ID
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "tags",
            "created_at",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    # Anidamos las tareas que pertenecen a este proyecto
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "tasks", "created_at"]
