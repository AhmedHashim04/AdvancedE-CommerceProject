
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
 
@receiver(post_save, sender=Order)
def order_status_updated(sender, instance, created, **kwargs):
    """
    Send notification when an order status is updated.
    """
    if not created:
        subject = _("Modyex:Your order %(id)s status updated") % {'id': instance.id}
        message = _(
            "Hi %(username)s,\n"
            "Your order status is now: %(status)s.\n"
        ) % {
            'username': instance.user.username,
            'status': instance.get_status_display(),  
        }

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=True,
        )
