from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.conf import settings
from apps.sellers.models import Seller
from decimal import Decimal
# ---------------- Promotion Base ----------------

class PromotionEngine:
    def __init__(self, cart, user=None):
        self.cart = cart
        self.user = user

    def apply_promotions(self):
        total_discount = Decimal("0.00")
        for promotion in Promotion.objects.filter(is_active=True):
            if not promotion.can_be_applied(self.user):
                continue
            discount = self._apply_promotion_to_cart(promotion)
            total_discount += discount
        return total_discount

    def _apply_promotion_to_cart(self, promotion):
        if promotion.apply_to == Promotion.ApplyToChoices.PRODUCTS:
            return self._apply_to_products(promotion)
        elif promotion.apply_to == Promotion.ApplyToChoices.ALL:
            return self._apply_to_all(promotion)
        return Decimal("0.00")


class Promotion(models.Model):

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED_AMOUNT = "fixed", "Fixed Amount"
        FREE_SHIPPING = "shipping", "Free Shipping"
        GIFT = "gift", "Gift with Purchase"
        BXGY = "bxgy", "Buy X Get Y Free"

    class ApplyToChoices(models.TextChoices):
        PRODUCTS = 'products', 'Specific Products'
        TAGS = 'tags', 'Specific Tags'
        CATEGORIES = 'categories', 'Specific Categories'
        ORDER = 'order', 'Entire Order'
        ALL = 'all', 'All Products'

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="promotions")
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    apply_to = models.CharField(max_length=20, choices=ApplyToChoices.choices, default=ApplyToChoices.ALL)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    max_usage = models.PositiveIntegerField(blank=True, null=True, help_text="Max total usage of this promotion")
    max_usage_per_user = models.PositiveIntegerField(blank=True, null=True, help_text="Max usage per user")

    class Meta:
        indexes = [
            models.Index(fields=['discount_type']),
            models.Index(fields=['is_active', 'start_date', 'end_date']),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")
        if self.value is not None and self.value < 0:
            raise ValidationError("Discount value must be positive.")
        if self.max_usage is not None and self.max_usage < 0:
            raise ValidationError("Max usage must be positive.")
        if self.max_usage_per_user is not None and self.max_usage_per_user < 0:
            raise ValidationError("Max usage per user must be positive.")

    @property
    def is_expired(self):
        if self.end_date and timezone.now() > self.end_date:
            return True
        return False

    def can_be_applied(self, user=None):
        if not self.is_active or self.is_expired:
            return False
        if self.max_usage is not None:
            from django.db.models import Count
            total_used = self.usages.count()
            if total_used >= self.max_usage:
                return False
        if user and self.max_usage_per_user is not None:
            used_by_user = self.usages.filter(user=user).count()
            if used_by_user >= self.max_usage_per_user:
                return False
        return True

# ---------------- Promotion Usage ----------------
class PromotionUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=255, blank=True, null=True, help_text="For guest users")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='usages')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    product = models.ForeignKey('store.Product', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.promotion.name} used on Order {self.order.id}"

# ---------------- BXGY Promotion ----------------
class BXGYPromotion(models.Model):
    promotion = models.OneToOneField(Promotion, on_delete=models.CASCADE, related_name='bxgy')
    buy_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    get_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    def clean(self):
        if self.buy_quantity <= 0:
            raise ValidationError("Buy quantity must be greater than 0")
        if self.get_quantity < 0:
            raise ValidationError("Get quantity cannot be negative")

# ---------------- Gift Promotion ----------------
class GiftPromotion(models.Model):
    promotion = models.OneToOneField(Promotion, on_delete=models.CASCADE, related_name='gift')
    gift_product = models.ForeignKey('store.Product', on_delete=models.SET_NULL, null=True, blank=True)
    gift_quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

# ---------------- Promotion Config (Optional Extra Constraints) ----------------
class PromotionConfig(models.Model):
    promotion = models.OneToOneField(Promotion, on_delete=models.CASCADE, related_name='config')
    min_quantity = models.PositiveIntegerField(blank=True, null=True)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    def is_satisfied(self, order_items, order_total):
        if self.min_quantity and sum(item.quantity for item in order_items) < self.min_quantity:
            return False
        if self.min_order_value and order_total < self.min_order_value:
            return False
        return True
