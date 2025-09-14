from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL,unique=True, on_delete=models.CASCADE, related_name='shipping_companies', verbose_name=_("User"))
    name = models.CharField(max_length=100, verbose_name=_("Shipping Company Name"))
    company_description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='shipping_logos/', null=True, blank=True)
    address = models.ForeignKey("shipping.Address", verbose_name=_("Address"), on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Shipping Company")
        verbose_name_plural = _("Shipping Companies")
    
    def __str__(self):
        return self.name
    
class ShippingPlan(models.Model):
    company = models.ForeignKey(ShippingCompany, on_delete=models.CASCADE, related_name='plans')
    governorate = models.ManyToManyField(Governorate, related_name='shipping_plans')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Base Price"))
    estimated_days = models.PositiveIntegerField(verbose_name=_("Estimated Delivery Days"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Shipping Plan")
        verbose_name_plural = _("Shipping Plans")
    
    def __str__(self):
        return f"{self.company.name} - {self.governorate.name_ar}"
        
class WeightPricingTier(models.Model):
    plan = models.ForeignKey(ShippingPlan, on_delete=models.CASCADE, related_name='weight_tiers')
    min_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Minimum Weight (kg)"))
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Maximum Weight (kg)"))
    price_per_kilo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price per Kilo (EGP)"))

    
    class Meta:
        verbose_name = _("Weight Pricing Tier")
        verbose_name_plural = _("Weight Pricing Tiers")
        ordering = ['min_weight']
    
    def __str__(self):
        max_weight = self.max_weight or _("Above")
        return f"{self.min_weight} - {max_weight} kg: {self.price_per_kilo} EGP"
    


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
        if not self.tracking_number:
            self.tracking_number = f"TRK{self.id:08d}"
        super().save(*args, **kwargs)

class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Weight (kg)")
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Volume (cm³)", null=True, blank=True)
    
    class Meta:
        verbose_name = "Shipment Item"
        verbose_name_plural = "Shipment Items"
        unique_together = ('shipment', 'order_item')
    
    def __str__(self):
        return f"{self.order_item.product.name} in Shipment #{self.shipment.id}"