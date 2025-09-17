from django.db import models
# from django.utils import timezone
# from apps.orders.models import Order
# from django.utils.translation import gettext_lazy as _
# 

# class Payment(models.Model):
#     STATUS_CHOICES = [
#         ("pending", "Pending"),
#         ("success", "Success"),
#         ("failed", "Failed"),
#     ]

#     order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     card_number = models.CharField(max_length=16)
#     card_holder = models.CharField(max_length=100)
#     expiration_date = models.CharField(max_length=5)  # MM/YY
#     cvv = models.CharField(max_length=4)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     created_at = models.DateTimeField(default=timezone.now)



class PaymentMethod(models.TextChoices):
    PAYPAL = "paypal", _("PayPal")
    PAYMOB = "paymob", _("Paymob")
    STRIPE = "stripe", _("Stripe")
    CASH_ON_DELIVERY = "cod", _("Cash on Delivery")
