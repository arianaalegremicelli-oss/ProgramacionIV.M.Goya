# Fragmento de taskflow/core/serializers.py  –  cambios de la Clase 5
# Alumna: Ariana Alegre Micelli
#
# Agregar al TaskSerializer existente el campo calculado due_on_holiday:

import nh3  # (se instala en la Clase 8; aquí sólo se muestra la estructura)
from rest_framework import serializers

from .models import Task, Tag
from .services import HolidayService


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    tags           = TagSerializer(many=True, read_only=True)
    due_on_holiday = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = [
            "id", "project", "title", "description", "priority",
            "status", "due_date", "due_on_holiday", "tags", "created_at",
        ]

    def get_due_on_holiday(self, obj):
        if not obj.due_date:
            return False
        return HolidayService.is_holiday(obj.due_date)

    def validate_due_date(self, value):
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("La fecha límite no puede estar en el pasado.")
        return value

    def validate(self, data):
        # Si se intenta marcar completada sin fecha límite, se rechaza.
        if data.get("status") == "completada" and not data.get("due_date"):
            raise serializers.ValidationError(
                "No se puede completar una tarea sin fecha límite."
            )
        return data
