import uuid

from django.utils.translation import gettext_lazy as _
from apps.store.models import Product
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from apps.sellers.models import Seller

class OrderStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PROCESSING = "processing", _("Processing")
    SHIPPED = "shipped", _("Shipped")
    DELIVERED = "delivered", _("Delivered")
    CANCELLED = "cancelled", _("Cancelled")
    RETURNED = "returned", _("Returned")
    FAILED = "failed", _("Failed")


# class ShippingClass(models.TextChoices):
#     STANDARD = "standard", _("Standard Shipping")
#     PICKUP = "pickup", _("In-store Pickup")
#     EXPRESS = "express", _("Express Shipping")

class Order(models.Model):

    id = models.UUIDField(_("ID"), primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders", verbose_name=_("User"))
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"), blank=True, null=True)

    address = models.ForeignKey("accounts.Address", on_delete=models.PROTECT, related_name="orders", verbose_name=_("Address"))
    full_name = models.CharField(max_length=100, verbose_name=_("Full Name"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Additional Notes"))
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, verbose_name=_("Status"))
    # shipping_method = models.CharField(max_length=20, choices=ShippingClass.choices, default=ShippingClass.STANDARD, verbose_name=_("Shipping Method"))
    
    # shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Shipping Cost"))
    weight_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Delivery Fee"))
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Total Price"))
    paid = models.BooleanField(verbose_name=_("Paid"), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    invoice_pdf = models.FileField(upload_to="invoices/", null=True, blank=True, verbose_name=_("Invoice PDF"))

    status_changed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Status Changed At"))

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

    # def calculate_shipping(self):
    #     total_shipping = sum(item.shipping_cost for item in self.items.all())
    #     self.shipping_cost = total_shipping
    #     if self.shipping_method == ShippingClass.EXPRESS:
    #         self.shipping_cost += Decimal('20.00')
    #     elif self.shipping_method == ShippingClass.STANDARD:
    #         self.shipping_cost += Decimal('0.00')
    #     elif self.shipping_method == ShippingClass.PICKUP:
    #         self.shipping_cost += Decimal('0.00')
        
    #     self.save()

    def clean(self):
        if self.total_price < 0 :#or self.shipping_cost < 0:
            raise ValidationError(_("Prices must be non-negative."))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Discount"))
    # shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0) 

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    # def calculate_shipping_cost(self):

    #     if self.product.free_shipping:
    #         self.shipping_cost = 0

    #     elif self.product.shipping_cost is not None:
    #         self.shipping_cost = (self.product.shipping_cost + self.product.price_per_kilogram) * self.quantity


    def save(self, *args, **kwargs):
        # self.calculate_shipping_cost()
        super().save(*args, **kwargs)