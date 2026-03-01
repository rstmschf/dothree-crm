import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        await self.accept()

        self.room_group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        is_management = getattr(user, "role", None) in ("admin", "manager")
        if is_management:
            await self.channel_layer.group_add("management_group", self.channel_name)

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def send_notification(self, event):
        message = event["message"]
        notification_type = event.get("notification_type", "general")

        await self.send(
            text_data=json.dumps({"type": notification_type, "message": message})
        )


class DealConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.deal_id = self.scope["url_route"]["kwargs"]["deal_id"]
        self.room_group_name = f"deal_{self.deal_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def new_comment(self, event):
        comment_data = event["message"]

        await self.send(
            text_data=json.dumps({"type": "new_comment", "comment": comment_data})
        )
