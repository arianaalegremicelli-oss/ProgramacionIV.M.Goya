# Fragmento de taskflow/core/models.py  –  cambios de la Clase 6
# Alumna: Ariana Alegre Micelli
#
# Agregar al modelo Task:

from django.conf import settings
from django.db import models


class Task(models.Model):
    # ... campos previos (project, title, description, etc.) ...

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
    )

    # Después de agregar el campo:
    # python manage.py makemigrations core
    # python manage.py migrate
