from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                             related_name='addresses',blank=True,null=True,verbose_name=_("User")) # for Guest checkout
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"), blank=True, null=True)
    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"),help_text=_("Full Name"))
    phone_number = models.CharField(max_length=20,help_text=_("Primary Phone Number"), verbose_name=_("Phone Number"))
    alternate_phone = models.CharField(max_length=11,blank=True,help_text=_("Alternate Phone Number (optional)"),
                                       verbose_name=_("Alternate Phone Number (optional)"),)
    governorate = models.ForeignKey("Governorate", on_delete=models.CASCADE, verbose_name=_("Governorate"))
    city = models.ForeignKey("City", on_delete=models.CASCADE, verbose_name=_("City"))
    village = models.CharField(max_length=100,help_text=_("Village (optional if you from city center) "),verbose_name=_("Village"),blank=True, null=True)
    detailed_address = models.CharField(max_length=255, verbose_name=_("Detailed Address "),help_text=_("Write detailed address that you want to deliver the order "))
    postal_code = models.CharField(max_length=20,help_text=_("you can leave it empty if you don't know what postal code"), verbose_name=_("Postal Code"))
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.detailed_address}, {self.city}"

class Governorate(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_("Governorate Name (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Governorate Name (English)"))
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Governorate Code"))
    
    class Meta:
        verbose_name = _("Governorate")
        verbose_name_plural = _("Governorates")
    
    def __str__(self):
        return self.name_ar

class City(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='cities')
    name_ar = models.CharField(max_length=100, verbose_name=_("City Name (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("City Name (English)"))
    code = models.CharField(max_length=10, verbose_name=_("City Code"))
    
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        unique_together = ('governorate', 'code')
    
    def __str__(self):
        return f"{self.name_ar} - {self.governorate.name_ar} "

class ShippingCompany(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,unique=True, on_delete=models.CASCADE, related_name='shipping_company', verbose_name=_("User"))
    company_name = models.CharField(max_length=150, unique=True)
    company_description = models.TextField(blank=True, null=True)
    company_email = models.EmailField(unique=True, blank=True, null=True)
    company_phone = models.CharField(max_length=20)
    company_address = models.ForeignKey("shipping.Address", verbose_name=_("Address"), on_delete=models.CASCADE, blank=True, null=True)
    logo = models.ImageField(upload_to='shipping_logos/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_shipping_plan(self, governorate):
        plans = self.plans.filter(governorate=governorate, is_active=True)
        return plans.first()  
    
    class Meta:
        verbose_name = _("Shipping Company")
        verbose_name_plural = _("Shipping Companies")
    
    def __str__(self):
        return self.company_name


class ShippingPlan(models.Model):
    company = models.ForeignKey(ShippingCompany, on_delete=models.CASCADE, related_name='plans')
    governorates = models.ManyToManyField(Governorate, related_name='shipping_plans')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Base Price"))
    estimated_days = models.PositiveIntegerField(verbose_name=_("Estimated Delivery Days"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Shipping Plan")
        verbose_name_plural = _("Shipping Plans")


    def __str__(self):
        governorates = self.governorates.values_list("name_ar", flat=True)
        return f"{self.company.company_name} - {', '.join(governorates)} - {self.base_price} EGP"

class WeightPricing(models.Model):
    plan = models.OneToOneField(ShippingPlan, unique=True, on_delete=models.CASCADE, related_name='weight_pricing')
    min_weight = models.DecimalField(help_text="Minimum weight in kg", max_digits=10, decimal_places=2, verbose_name=_("Minimum Weight (kg)"))
    price_per_kilo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price per Kilo (EGP)"))

    
    class Meta:
        verbose_name = _("Weight Pricing")
        verbose_name_plural = _("Weight Pricing")
        ordering = ['min_weight']

    def shipping_plan_weight_cost(self, total_weight):
        if not self.min_weight:
            return 0
        if total_weight > self.min_weight:
                return self.price_per_kilo * total_weight
        return 0

    def __str__(self):
        return f"{self.min_weight}: {self.price_per_kilo} EGP"
    
    def clean(self):
        if self.min_weight < 0:
            raise ValidationError("Minimum weight must be non-negative.")
        if self.price_per_kilo < 0:
            raise ValidationError("Price per kilo must be non-negative.")

class Shipment(models.Model):
    SHIPMENT_STATUS = (
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name='shipments')

    seller = models.ForeignKey("sellers.Seller", on_delete=models.CASCADE)
    company = models.ForeignKey("shipping.ShippingCompany", on_delete=models.CASCADE)

    shipping_plan = models.ForeignKey("shipping.ShippingPlan", on_delete=models.CASCADE)
    customer_address = models.ForeignKey("shipping.Address", on_delete=models.CASCADE, related_name='shipments')

    tracking_number = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS, default='pending')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Shipping Cost")
    estimated_delivery = models.DateField(null=True, blank=True, verbose_name="Estimated Delivery Date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Shipment"
        verbose_name_plural = "Shipments"

    def __str__(self):
        return f"Shipment #{self.id} for Order #{self.order.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.tracking_number:
            self.tracking_number = f"TRK{self.id:08d}"
            super().save(update_fields=["tracking_number"])



class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Weight (kg)")
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Volume (cm³)", null=True, blank=True)
    
    class Meta:
        verbose_name = "Shipment Item"
        verbose_name_plural = "Shipment Items"
        unique_together = ('shipment', 'order_item')
    
    def __str__(self):
        return f"{self.order_item.product.name} in Shipment #{self.shipment.id}"