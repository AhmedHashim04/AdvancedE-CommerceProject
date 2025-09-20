# apps/notifications/services.py
from .models import Notification, NotificationRecipient
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

def create_order_notifications(order):
    # example: create notification for buyer + sellers (multi-seller split)
    notif = Notification.objects.create(
        actor=order.user,
        verb='New order created',
        notif_type='order_created',
        description=f'Order #{order.pk} created',
        content_type=ContentType.objects.get_for_model(order),
        object_id=str(order.pk),
        data={'order_id': order.pk, 'total': str(order.total)}
    )
    recipients = [order.user] + [item.seller for item in order.items.all()]  # example
    recipients = list(set(recipients))
    rec_objs = []
    for r in recipients:
        rec_objs.append(NotificationRecipient(notification=notif, recipient=r))
    NotificationRecipient.objects.bulk_create(rec_objs)

    # send real-time via channel layer for online users (group per user)
    for r in recipients:
        async_to_sync(channel_layer.group_send)(
            f'user_{r.pk}',
            {
                'type': 'notify.message',
                'message': {
                    'notification_id': notif.pk,
                    'notif_type': notif.notif_type,
                    'verb': notif.verb,
                    'data': notif.data,
                    'created_at': str(notif.created_at),
                }
            }
        )

    # Optionally: enqueue push tasks for offline users using Celery
