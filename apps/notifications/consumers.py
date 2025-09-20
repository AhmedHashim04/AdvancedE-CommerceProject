# apps/notifications/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
import json

User = get_user_model()

class NotificationsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # auth token from query string ?token=...
        qs = parse_qs(self.scope['query_string'].decode())
        token = qs.get('token', [None])[0]
        user = None
        if token:
            try:
                # Validate token (example for simplejwt)
                UntypedToken(token)
                # decode to get user id (omitted for brevity) - use your JWT decode logic
                from rest_framework_simplejwt.backends import TokenBackend
                token_backend = TokenBackend(algorithm='HS256')
                valid_data = token_backend.decode(token)
                user_id = valid_data['user_id']
                user = await database_sync_to_async(User.objects.get)(pk=user_id)
            except Exception:
                user = None

        if user is None:
            await self.close()
        else:
            self.user = user
            self.group_name = f'user_{user.pk}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify_message(self, event):
        # event from group_send
        await self.send_json(event['message'])

    async def receive_json(self, content, **kwargs):
        # optional: handle client messages e.g., mark read via WS
        if content.get('action') == 'mark_read':
            notif_id = content.get('notification_id')
            # update DB (call sync_to_async)...
            # then acknowledge
            await self.send_json({'status':'ok','action':'marked','notification_id':notif_id})
