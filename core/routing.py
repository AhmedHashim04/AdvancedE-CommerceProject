# project/routing.py
from django.urls import re_path
from apps.notifications.consumers import NotificationsConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/?$', NotificationsConsumer.as_asgi()),
]
