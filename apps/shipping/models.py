from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order, OrderItem
from apps.sellers.models import Seller

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
        return f"{self.name_ar} - {self.governorate.name_ar}"

class ShippingCompany(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_("Shipping Company Name (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Shipping Company Name (English)"))
    logo = models.ImageField(upload_to='shipping_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Shipping Company")
        verbose_name_plural = _("Shipping Companies")
    
    def __str__(self):
        return self.name_ar
class ShippingPlan(models.Model):
    company = models.ForeignKey(ShippingCompany, on_delete=models.CASCADE, related_name='plans')
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='shipping_plans')
    cities = models.ManyToManyField(City, blank=True, related_name='shipping_plans')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Base Price"))
    estimated_days = models.PositiveIntegerField(verbose_name=_("Estimated Delivery Days"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Shipping Plan")
        verbose_name_plural = _("Shipping Plans")
        unique_together = ('company', 'governorate')
    
    def __str__(self):
        return f"{self.company.name_ar} - {self.governorate.name_ar}"
    
class WeightPricingTier(models.Model):
    plan = models.ForeignKey(ShippingPlan, on_delete=models.CASCADE, related_name='weight_tiers')
    min_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Minimum Weight (kg)"))
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Maximum Weight (kg)"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price for Specified Weight"))

    
    class Meta:
        verbose_name = _("Weight Pricing Tier")
        verbose_name_plural = _("Weight Pricing Tiers")
        ordering = ['min_weight']
    
    def __str__(self):
        max_weight = self.max_weight or _("Above")
        return f"{self.min_weight} - {max_weight} kg: {self.price} EGP"
    


class Shipment(models.Model):
    SHIPMENT_STATUS = (
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('in_transit', 'قيد التوصيل'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    shipping_plan = models.ForeignKey(ShippingPlan, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS, default='pending')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="تكلفة الشحن")
    estimated_delivery = models.DateField(null=True, blank=True, verbose_name="موعد التسليم المتوقع")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "شحنة"
        verbose_name_plural = "الشحنات"
    
    def __str__(self):
        return f"شحنة #{self.id} للطلب #{self.order.id}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            # إنشاء رقم تتبع فريد
            self.tracking_number = f"TRK{self.id:08d}"
        super().save(*args, **kwargs)

class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "عنصر الشحنة"
        verbose_name_plural = "عناصر الشحنة"
        unique_together = ('shipment', 'order_item')
    
    def __str__(self):
        return f"{self.order_item.product.name_ar} في الشحنة #{self.shipment.id}"