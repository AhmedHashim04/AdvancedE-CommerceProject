

# Storage (history)
# Real-time: Django Channels + Redis channel_layer → WebSockets
# Push Notifications: FCM (Firebase Cloud Messaging) / APNs (Apple Push Notification service)

# apps/notifications/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    NOTIF_TYPES = [
        ('order_created','order_created'),
        ('order_shipped','order_shipped'),
        ('new_message','new_message'),
        ('seller_approved','seller_approved'),
        ('shipping_company_approved','shipping_company_approved'),
        ('tag_approved','tag_approved'),
        ('brand_approved','brand_approved'),
        ('category_approved','category_approved'),
        ('promotion_approved','promotion_approved'),
        ('product_reviewed','product_reviewed'),
        ('product_returned','product_returned'),
        ('product_stock_low','product_stock_low'),
        ]
    
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='actor_notifications')
    verb = models.CharField(max_length=64)  # human readable short verb
    notif_type = models.CharField(max_length=50, choices=NOTIF_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    # optional generic relation to link to order/product/etc
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)  # payload for frontend (IDs, urls, meta)
    # indexes for queries
    class Meta:
        ordering = ['-created_at']

class NotificationRecipient(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    delivered = models.BooleanField(default=False)  # whether pushed via websocket / push
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['recipient','is_read']),
            models.Index(fields=['recipient','created_at']),
        ]
