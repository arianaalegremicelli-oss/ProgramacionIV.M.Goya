from datetime import date
from rest_framework import serializers
from .models import Project, Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
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

    def validate_due_date(self, value):
        # Validacion por campo individual: la fecha no puede ser en el pasado
        if value and value < date.today():
            raise serializers.ValidationError("La fecha limite no puede ser en el pasado.")
        return value

    def validate(self, data):
        # Tomamos los valores nuevos o los que ya existian si estamos actualizando
        status_val = data.get("status", self.instance.status if self.instance else None)
        due_date_val = data.get("due_date", self.instance.due_date if self.instance else None)
        project = data.get("project", self.instance.project if self.instance else None)

        # Regla 1: completada requiere due_date
        if status_val == "completada" and not due_date_val:
            raise serializers.ValidationError(
                "No se puede marcar una tarea como completada sin fecha limite registrada."
            )

        # Regla 2 (Tarea para la casa): una tarea no puede estar en 'en_progreso'
        # si su proyecto no tiene al menos una tarea 'completada' previamente.
        if status_val == "en_progreso":
            if project:
                completadas = project.tasks.filter(status="completada")
                if self.instance:
                    completadas = completadas.exclude(pk=self.instance.pk)
                if not completadas.exists():
                    raise serializers.ValidationError(
                        "Una tarea no puede tener status 'en_progreso' si su proyecto no tiene ninguna tarea completada todavia."
                    )

        return data


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "tasks", "created_at"]
