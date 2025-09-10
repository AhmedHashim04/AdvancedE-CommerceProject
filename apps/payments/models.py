from django.db import models
from django.utils import timezone
from apps.orders.models import Order
from django.utils.translation import gettext_lazy as _

class PaymentMethod(models.TextChoices):
    VISA = "visa", _("Visa")
    MASTERCARD = "mastercard", _("MasterCard")
    AMEX = "amex", _("American Express")
    MEEZA = "meeza", _("Meeza")

    APPLE_PAY = "apple_pay", _("Apple Pay")
    GOOGLE_PAY = "google_pay", _("Google Pay")
    PAYPAL = "paypal", _("PayPal")

    CASH_ON_DELIVERY = "cod", _("Cash on Delivery")

    INSTALLMENTS = "installments", _("Installments")
    BNPL_VALU = "bnpl_valu", _("Buy Now Pay Later (valU)")
    BNPL_TABBY = "bnpl_tabby", _("Buy Now Pay Later (Tabby)")


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=50, choices=PaymentMethod.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)