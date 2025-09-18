from django.db import models
# from django.utils import timezone
from apps.orders.models import Order
from apps.sellers.models import Seller
from django.utils.translation import gettext_lazy as _
# 

# class Payment(models.Model):
#     STATUS_CHOICES = [
#         ("pending", "Pending"),
#         ("success", "Success"),
#         ("failed", "Failed"),
#     ]

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


