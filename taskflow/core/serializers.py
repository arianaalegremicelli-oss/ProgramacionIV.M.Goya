# taskflow/core/serializers.py
# Alumna: Ariana Alegre Micelli

import nh3
from django.utils import timezone
from rest_framework import serializers

from .models import Project, Tag, Task
from .services import HolidayService


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "created_at"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    due_on_holiday = serializers.SerializerMethodField()

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
            "due_on_holiday",
            "tags",
            "created_at",
        ]

    def get_due_on_holiday(self, obj):
        if not obj.due_date:
            return False
        return HolidayService.is_holiday(obj.due_date)

    def validate_due_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("La fecha límite no puede estar en el pasado.")
        return value

    def validate_description(self, value):
        # Sanitización estricta contra ataques XSS
        return nh3.clean(value, tags=set())

    def validate(self, data):
        if data.get("status") == "completada" and not data.get("due_date"):
            raise serializers.ValidationError(
                "No se puede completar una tarea sin fecha límite."
            )
        return data
