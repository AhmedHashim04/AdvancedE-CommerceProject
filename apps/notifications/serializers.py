# apps/notifications/serializers.py
from rest_framework import serializers
from .models import NotificationRecipient

class NotificationRecipientSerializer(serializers.ModelSerializer):
    notification = serializers.SerializerMethodField()
    class Meta:
        model = NotificationRecipient
        fields = ['id','is_read','read_at','created_at','notification']

    def get_notification(self, obj):
        n = obj.notification
        return {
            'id': n.pk,
            'verb': n.verb,
            'type': n.notif_type,
            'data': n.data,
            'created_at': n.created_at
        }
