from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=150, unique=True)
    store_description = models.TextField(blank=True, null=True)
    store_email = models.EmailField(unique=True, blank=True, null=True)
    store_phone = models.CharField(max_length=20)
    store_address = models.ForeignKey("shipping.Address", verbose_name=_("Address"), on_delete=models.CASCADE, blank=True, null=True)
    default_shipping_company = models.ForeignKey("shipping.ShippingCompany", on_delete=models.PROTECT, verbose_name="Default Shipping Company")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Seller")
        verbose_name_plural = _("Sellers")

    def __str__(self):
        return self.store_name


class SubOrder(models.Model):
    """Logical grouping inside an Order for a single seller.
    Each SubOrder will correspond to a PayPal purchase_unit.
    """
    order = models.ForeignKey("orders.Order", related_name="sub_orders", on_delete=models.CASCADE)
    seller = models.ForeignKey("sellers.Seller",related_name="sub_orders", on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=32, default="pending")

    class Meta:
        verbose_name = "SubOrder"
        verbose_name_plural = "SubOrders"


    def __str__(self):
        return f"SubOrder #{self.id} of Order {self.order.id} for {self.seller}"
