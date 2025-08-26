from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.sellers.models import Seller

User = get_user_model()

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", _("Percentage")
        FIXED_AMOUNT = "fixed", _("Fixed Amount")
        FREE_SHIPPING = "shipping", _("Free Shipping")

        # Bundle = 'bundle', _('Bundle Discount'),
        # BXGY = "bxgy", _("Buy X Get Y Free")
        # BXGY_Discount = "bxgy_discount", _("Buy X Get Y at Discount")
        # GIFT = "gift", _("Gift with Purchase")
        # TIERED = "tiered", _("Tiered Discount")
    code = models.CharField(max_length=50, unique=True, db_index=True, help_text=_("Coupon code used by customers"))
    description = models.TextField(blank=True, null=True)

    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name="coupon")

    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
                                help_text=_("Percentage (0-100) or fixed amount"))

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)

    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    allowed_users = models.ManyToManyField(User, blank=True, related_name="coupons")
    gift_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_type})"

    def clean(self):
        if self.discount_type == self.DiscountType.PERCENTAGE and self.value > 100:
            raise ValidationError("Percentage discount cannot exceed 100%.")

    # ------------------- Validation -------------------
    def is_valid(self, cart_total, user=None):
        
        now = timezone.now()
        if not self.is_active:
            return False, "Coupon is not active."
        if not (self.start_date <= now <= self.end_date):
            return False, "Coupon is not valid at this time."
        if self.usage_limit and self.redemptions.count() >= self.usage_limit:
            return False, "Coupon usage limit reached."
        if user and self.usage_limit_per_user:
            if self.redemptions.filter(user=user).count() >= self.usage_limit_per_user:
                return False, "You have reached the usage limit for this coupon."
        if self.allowed_users.exists() and (not user or user not in self.allowed_users.all()):
            return False, "This coupon is not allowed for your account."
        if self.minimum_order_amount and cart_total is not None and cart_total < self.minimum_order_amount:
            return False, f"Order total must be at least {self.minimum_order_amount} to use this coupon."
        return True, None

class CouponRedemption(models.Model):

    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE,related_name="redemptions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} used by {self.user}"


# Full Scenarios for Discount Types:
    # seller will add promotion to his product 
    # promotion is applied on product
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 