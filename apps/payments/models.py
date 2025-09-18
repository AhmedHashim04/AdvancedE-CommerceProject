from decimal import Decimal
from django.db import models
# from django.utils import timezone
from apps.orders.models import Order
from apps.sellers.models import Seller
from django.utils.translation import gettext_lazy as _




class Payment(models.Model):
    """Stores PayPal order / capture ids and raw response for audit."""
    order = models.ForeignKey("orders.Order", related_name="payments", on_delete=models.CASCADE)
    paypal_order_id = models.CharField(max_length=255, null=True, blank=True)
    paypal_capture_id = models.CharField(max_length=255, null=True, blank=True)
    provider = models.CharField(max_length=50, default="paypal")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=8, default="EGP")
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Payment {self.provider} - {self.paypal_order_id or self.paypal_capture_id}"


class PaymentMethod(models.TextChoices):
    PAYPAL = "paypal", _("PayPal")
    PAYMOB = "paymob", _("Paymob")
    STRIPE = "stripe", _("Stripe")
    CASH_ON_DELIVERY = "cod", _("Cash on Delivery")


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    status = models.CharField(max_length=50)
    method = models.CharField(max_length=50, choices=PaymentMethod.choices, default=PaymentMethod.PAYMOB)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class SellerPayout(Payment):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="payouts")

    def get_items(self):
        return self.order.get_items().filter(product__seller=self.seller)


