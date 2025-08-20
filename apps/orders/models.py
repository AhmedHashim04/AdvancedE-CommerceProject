import uuid

from django.utils.translation import gettext_lazy as _
from ..store.models import Product
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class OrderStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PROCESSING = "processing", _("Processing")
    SHIPPED = "shipped", _("Shipped")
    DELIVERED = "delivered", _("Delivered")
    CANCELLED = "cancelled", _("Cancelled")
    RETURNED = "returned", _("Returned")
    FAILED = "failed", _("Failed")

class PaymentMethod(models.TextChoices):
    COD = "cod", _("Cash on Delivery")
    CREDIT_CARD = "credit_card", _("Credit Card")
    DEBIT_CARD = "debit_card", _("Debit Card")
    PAYPAL = "paypal", _("PayPal")
    APPLE_PAY = "apple_pay", _("Apple Pay")
    GOOGLE_PAY = "google_pay", _("Google Pay")
    BANK_TRANSFER = "bank_transfer", _("Bank Transfer")
    STRIPE = "stripe", _("Stripe")
    AMAZON_PAY = "amazon_pay", _("Amazon Pay")
    KLARNA = "klarna", _("Klarna")
    AFTERPAY = "afterpay", _("Afterpay")
    BITCOIN = "bitcoin", _("Bitcoin")
    OTHER_CRYPTO = "other_crypto", _("Other Cryptocurrency")
    ALIPAY = "alipay", _("Alipay")
    WECHAT_PAY = "wechat_pay", _("WeChat Pay")
    VENMO = "venmo", _("Venmo")
    SQUARE = "square", _("Square")
    PAYONEER = "payoneer", _("Payoneer")
    SHOP_PAY = "shop_pay", _("Shop Pay")
    IDEAL = "ideal", _("iDEAL")
    SOFORT = "sofort", _("Sofort")
    GIROPAY = "giropay", _("Giropay")
    BOLETO = "boleto", _("Boleto")
    PIX = "pix", _("Pix")
    
class ShippingClass(models.TextChoices):
    STANDARD = "standard", _("Standard Shipping")
    PICKUP = "pickup", _("In-store Pickup")
    EXPRESS = "express", _("Express Shipping")

class Order(models.Model):

    id = models.UUIDField(_("ID"), primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders", verbose_name=_("User"))
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"), blank=True, null=True)

    address = models.ForeignKey("accounts.Address", on_delete=models.PROTECT, related_name="orders", verbose_name=_("Address"))
    full_name = models.CharField(max_length=100, verbose_name=_("Full Name"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Additional Notes"))
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, verbose_name=_("Status"))
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD, verbose_name=_("Payment Method"))
    shipping_method = models.CharField(max_length=20, choices=ShippingClass.choices, default=ShippingClass.STANDARD, verbose_name=_("Shipping Method"))

    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Shipping Cost"))
    weight_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Delivery Fee"))
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Total Price"))
    status_changed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Status Changed At"))
    paid = models.BooleanField(verbose_name=_("Paid"), default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    invoice_pdf = models.FileField(upload_to="invoices/", null=True, blank=True, verbose_name=_("Invoice PDF"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id}"
    
    
    def get_items(self):
        return self.items.all()

    def update_status(self, new_status):
        if self.status != new_status:
            self.status = new_status
            self.status_changed_at = timezone.now()
            self.save()

    # def calculate_weight_cost(self):
    #     total_quantity = sum(item.quantity for item in self.get_items())-3

    #     if total_quantity > 0:
    #         return Decimal(total_quantity) * 10
    #     return Decimal("0.00")


    def clean(self):
        if self.total_price < 0 or self.shipping_cost < 0:
            raise ValidationError(_("Prices must be non-negative."))

    def save(self, *args, **kwargs):
        if self.weight_cost == 0 :
            pass
            # self.weight_cost = self.calculate_weight_cost()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Discount"))

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    # @property
    # def price_after_discount(self):
    #     price = self.price if self.price is not None else Decimal("0.00")
    #     discount = self.discount if self.discount is not None else Decimal("0.00")
    #     return (price - discount).quantize(Decimal('0.01'))

    

    # @property
    # def total_item_price_after_discount(self):
        
    #     return (self.price_after_discount * self.quantity).quantize(Decimal('0.01'))