from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('bogo', 'Buy One Get One Free'),
        ('bxgy', 'Buy X Get Y Free'),
        ('bxgy_discount', 'Buy X Get Y at Discount'),
        ('bundle', 'Bundle Discount'),
        ('free_shipping', 'Free Shipping'),
        ('gift', 'Gift with Purchase'),
        ('tiered', 'Tiered Discount'),
    ]

    APPLY_TO_CHOICES = [
        ('products', 'Specific Products'),
        ('categories', 'Entire Categories'),
        ('all', 'All Products'),
    ]

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=50, blank=True, null=True, unique=True, db_index=True)  # دمج الكوبون
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True, null=True
    )

    # شروط التفعيل
    min_quantity = models.PositiveIntegerField(default=1, blank=True, null=True)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_usage = models.PositiveIntegerField(blank=True, null=True)
    max_usage_per_user = models.PositiveIntegerField(blank=True, null=True)

    # معلمات إضافية لأنواع محددة
    # for bxgy
    buy_quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Buy X quantity")
    get_quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Get Y quantity")

    # for bxgy_discount
    get_discount = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    # gift
    gift_product = models.ForeignKey(
        'store.Product',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='gift_promotions'
    )

    # نطاق التطبيق
    apply_to = models.CharField(max_length=20, choices=APPLY_TO_CHOICES, default='products')
    products = models.ManyToManyField('store.Product', blank=True)
    categories = models.ManyToManyField('store.Category', blank=True)
    excluded_products = models.ManyToManyField( #لو فيه منتجات معينة مستثناة من العرض حتى لو داخلة في الفئة.
        'store.Product',
        blank=True,
        related_name='excluded_promotions'
    )
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

    total_uses = models.PositiveIntegerField(default=0)

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

        if self.discount_type == 'bxgy' and not (self.buy_quantity and self.get_quantity):
            raise ValidationError("Buy X Get Y requires both buy and get quantities")

        if self.discount_type == 'bxgy_discount' and not (self.buy_quantity and self.get_quantity and not self.get_discount):
            raise ValidationError("Buy X Get Y requires both buy and get quantities")

    def __str__(self):
        return self.name

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


class FlashSale(models.Model):
    name = models.CharField(max_length=255)
    products = models.ManyToManyField('store.Product')
    discount_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_quantity = models.PositiveIntegerField(blank=True, null=True)
    purchases_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_ongoing(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}% off)"


class PromotionUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    product = models.ForeignKey('store.Product', on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.promotion.name} used on Order {self.order.id}"

