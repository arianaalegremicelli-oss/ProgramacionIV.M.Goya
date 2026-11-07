# taskflow/core/services.py
# Alumna: Ariana Alegre Micelli

import requests
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Task
from .repositories import TaskRepository


class TaskService:
    @staticmethod
    def mark_completed(task: Task) -> Task:
        """Marca una tarea como completada. Exige que tenga fecha límite."""
        if not task.due_date:
            raise ValidationError(
                "No se puede marcar una tarea como completada sin fecha límite registrada."
            )
        task.status = "completada"
        task.save(update_fields=["status"])
        return task

    @staticmethod
    def tasks_overdue(queryset=None):
        """Devuelve las tareas vencidas y no completadas del queryset dado."""
        if queryset is None:
            queryset = TaskRepository.get_queryset()
        today = timezone.now().date()
        return queryset.filter(due_date__lt=today).exclude(status="completada")


class ProjectService:
    @staticmethod
    def project_summary(project):
        """Devuelve la cantidad de tareas agrupadas por estado para el proyecto dado."""
        counts = project.tasks.values("status").annotate(total=Count("id"))
        result = {"pendiente": 0, "en_progreso": 0, "completada": 0}
        for row in counts:
            result[row["status"]] = row["total"]
        return result


class HolidayService:
    """Consulta feriados nacionales de Argentina usando date.nager.at con caché."""

    API_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/AR"

    @classmethod
    def get_holidays(cls, year: int) -> list[str]:
        cache_key = f"holidays_{year}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            response = requests.get(cls.API_URL.format(year=year), timeout=5)
            response.raise_for_status()
            dates = [item["date"] for item in response.json()]
            cache.set(cache_key, dates, timeout=60 * 60 * 24)  # 24 horas
        except (requests.RequestException, ValueError, KeyError):
            dates = []
            cache.set(cache_key, dates, timeout=60 * 5)  # Si falla, reintento en 5 min
        return dates

    @classmethod
    def is_holiday(cls, some_date) -> bool:
        return str(some_date) in cls.get_holidays(some_date.year)
