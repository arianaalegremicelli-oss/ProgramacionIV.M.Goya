# taskflow/core/consumers.py
# Alumna: Ariana Alegre Micelli

import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .services import MembershipService


class TaskNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket autenticado con JWT y presencia en tiempo real.
    Ruta: ws://host/ws/projects/<project_id>/?token=<access>
    """

    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.group_name = f"project_{self.project_id}"
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        is_member = await database_sync_to_async(MembershipService.is_member)(
            self.user, self.project_id
        )
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        self.joined = True
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "presence_update",
                "payload": {"user": self.user.username, "status": "online"},
            },
        )

    async def disconnect(self, close_code):
        if not getattr(self, "joined", False):
            return
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "presence_update",
                "payload": {"user": self.user.username, "status": "offline"},
            },
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({"echo": data}))

    async def task_notification(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
