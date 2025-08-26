from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.sellers.models import Seller

class Promotion(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", _("Percentage")
        FIXED_AMOUNT = "fixed", _("Fixed Amount")
        FREE_SHIPPING = "shipping", _("Free Shipping")

        GIFT = "gift", _("Gift with Purchase")
        BXGY = "bxgy", _("Buy X Get Y Free (e.g., Buy 5 Get 1 Free)")

    class ApplyToChoices(models.TextChoices):
        PRODUCTS = 'products', 'Specific Products'
        CATEGORIES = 'categories', 'Specific Categories'
        BRANDS = 'brands', 'Specific Brands'
        TAGS = 'tags', 'Specific Tags'
        ALL = 'all', 'All My Products'
    
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="promotions")

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType)
    value = models.DecimalField( #for bxgy_discount , MaxValueValidator(100)]
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True, null=True
    )
    

    # for BXGY = "bxgy", _("Buy X Get Y Free") 
    buy_quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Buy X quantity")
    get_quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Get Y quantity")


    # gift
    gift_product = models.ForeignKey(
        'store.Product',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='gift_promotions'
    )
#------------------------------------------------------
    # شروط التفعيل
    min_quantity = models.PositiveIntegerField(default=1, blank=True, null=True)
    min_order_value = models.DecimalField(default=1,max_digits=10, decimal_places=2, blank=True, null=True)
    max_usage_per_user = models.PositiveIntegerField(blank=True, null=True)

    max_usage = models.PositiveIntegerField(blank=True, null=True)
    total_uses = models.PositiveIntegerField(default=0)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    # الفعالية الزمنية
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # الأولوية وحالات التكرار
    priority = models.PositiveIntegerField(default=1, db_index=True)
    stackable = models.BooleanField(default=False) #لو True، ممكن دمجه مع عروض تانية. لو False، هو عرض مستقل.
    exclusive_group = models.CharField( #لو فيه عروض في نفس الـ group، ما ينفعش يجتمعوا مع بعض (حتى لو stackable=True).
        max_length=50, 
        blank=True,
        help_text="Promotions in the same group cannot be combined"
    )


    class Meta:
        indexes = [
            models.Index(fields=['discount_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        ordering = ['-priority']

    def clean(self):
        if self.discount_type in ['percentage', 'bxgy_discount'] and self.value is not None and self.value > 100:
            raise ValidationError({'value': "Percentage discount cannot exceed 100%."})

        if self.discount_type in ('bxgy', 'bxgy_discount') and not (self.buy_quantity and self.get_quantity):
            raise ValidationError("Buy X Get Y requires both buy and get quantities")
    
    def validate(self):
        now = timezone.now()
        if self.start_date and self.start_date > now:
            self.price = self.compare_at_price
            return False, "Promotion has not started yet."
        if self.end_date and self.end_date < now:
            self.price = self.compare_at_price
            return False, "Promotion has expired."
        if not self.is_active:
            self.price = self.compare_at_price
            return False, "Promotion is not active."
        if self.max_usage and self.total_uses >= self.max_usage:
            self.price = self.compare_at_price
            return False, "Promotion usage limit reached."
        return True

    def __str__(self):
        return self.name


    def is_ongoing(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}% off)"

class PromotionUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True) # for Guest
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"), blank=True, null=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    product = models.ForeignKey('store.Product', on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.promotion.name} used on Order {self.order.id}"

class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=255)
    points_per_purchase = models.PositiveIntegerField(default=1)
    points_per_currency = models.DecimalField(max_digits=5, decimal_places=2, default=0.01)
    redemption_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0.01)
    min_redemption_points = models.PositiveIntegerField(default=100)
    Eid_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=2.0, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LoyaltyPoints(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.points} points"


# User -- > cart apply coupon --> coupon verification in
#           total_price(fixed/percent) 
#           make order free shipping 
#           coupon check if specific product in cart quantity of product will be add +=1 or add specific other product
#           coupon check if 10 uses to this make code is dis active 
#           coupon check if total price is x dollar andit will apllied
#           