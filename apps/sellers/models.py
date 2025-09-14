from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_shipping_company = models.ForeignKey("shipping.ShippingCompany", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Default Shipping Company")
    store_name = models.CharField(max_length=150, unique=True)
    store_description = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.ForeignKey("shipping.Address", verbose_name=_("Address"), on_delete=models.CASCADE, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Seller")
        verbose_name_plural = _("Sellers")

    def __str__(self):
        return self.store_name

