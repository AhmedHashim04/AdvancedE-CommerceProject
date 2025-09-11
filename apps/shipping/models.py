from django.db import models
from django.utils.translation import gettext_lazy as _
from core.utils import COUNTRY_CHOICES



class ShippingSystem(models.Model):
    name = models.CharField(max_length=100, help_text=_("Shipping system name"))
    description = models.TextField(blank=True, null=True)

    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text=_("Base shipping fee"))
    per_kg_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text=_("Fee per KG"))

    estimated_delivery_days = models.PositiveIntegerField(default=3, help_text=_("Estimated delivery days"))
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text=_("Maximum weight allowed (kg)"))
    min_weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text=_("Minimum weight allowed (kg)"))

    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES,help_text=_("Country"),verbose_name=_("Country"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Shipping System")
        verbose_name_plural = _("Shipping Systems")

    def __str__(self):
        return f" - {self.name}"


