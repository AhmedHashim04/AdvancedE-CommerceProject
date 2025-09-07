from django.db import models
from django.conf import settings

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="notifications")

    verb = models.CharField(max_length=255)
    target = models.CharField(max_length=255, null=True, blank=True) 
    url = models.URLField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class UserNotified(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_notifications")
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="user_notifications")
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notification')
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user}: {self.notification.verb}"

    def mark_as_read(self):
        self.read = True
        self.save()



# @receiver(post_save, sender=Order)
# def order_created_notification(sender, instance, created, **kwargs):
#     if created:
#         Notification.objects.create(
#             recipient=instance.user,
#             actor=None,
#             verb="Your order has been placed",
#             target=f"Order #{instance.id}",
#             url=f"/orders/{instance.id}/"
#         )