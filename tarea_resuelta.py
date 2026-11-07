# Tarea de la Clase 5 — ProjectService con project_summary
# Alumna: Ariana Alegre Micelli

from django.db.models import Count
from .models import Task


class ProjectService:
    @staticmethod
    def project_summary(project):
        """
        Devuelve la cantidad de tareas por estado para el proyecto dado.

        Retorna un diccionario del tipo:
        {
            "pendiente":   <int>,
            "en_progreso": <int>,
            "completada":  <int>,
        }
        """
        counts = (
            project.tasks
            .values("status")
            .annotate(total=Count("id"))
        )
        result = {"pendiente": 0, "en_progreso": 0, "completada": 0}
        for row in counts:
            result[row["status"]] = row["total"]
        return result


# --- Agregar a ProjectViewSet en views.py ---
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from .services import ProjectService

# @action(detail=True, methods=["get"])
# def summary(self, request, pk=None):
#     """GET /api/projects/<id>/summary/"""
#     project = self.get_object()
#     data = ProjectService.project_summary(project)
#     return Response(data)
