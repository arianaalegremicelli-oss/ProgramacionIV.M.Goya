# taskflow/core/consumers.py
# Alumna: Ariana Alegre Micelli

import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Project


class TaskNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket asincrónico para notificaciones de proyectos en tiempo real.
    Ruta: ws://127.0.0.1:8000/ws/projects/<project_id>/
    """

    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.group_name = f"project_{self.project_id}"

        # Tarea resuelta: validar existencia del proyecto en BD sin bloquear el bucle de eventos
        existe = await self._project_exists()
        if not existe:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Modo echo de comprobación de conexión bidireccional
        await self.send(text_data=json.dumps({"echo": data}))

    async def task_notification(self, event):
        # Despacho de eventos entrantes desde el channel layer
        await self.send(text_data=json.dumps(event["payload"]))

    @database_sync_to_async
    def _project_exists(self) -> bool:
        return Project.objects.filter(id=self.project_id).exists()
