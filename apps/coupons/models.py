from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from cart.cart import Cart as ShoppingCart
User = get_user_model()

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", _("Percentage")
        FIXED_AMOUNT = "fixed", _("Fixed Amount")
        FREE_SHIPPING = "shipping", _("Free Shipping")
        BOGO = "bogo", _("Buy One Get One")
        GIFT = "gift", _("Gift Voucher")
        TIERED = "tiered", _("Tiered Discount")

    code = models.CharField(max_length=50, unique=True, db_index=True, help_text=_("Coupon code used by customers"))
    description = models.TextField(blank=True, null=True)

    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
                                help_text=_("Percentage (0-100) or fixed amount"))

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)

    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    applicable_categories = models.ManyToManyField("store.Category", blank=True, related_name="coupons")
    applicable_products = models.ManyToManyField("store.Product", blank=True, related_name="coupons")
    applicable_brands = models.ManyToManyField("store.Brand", blank=True, related_name="coupons")

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
    def is_valid(self, user=None,  date=None):
        now = date or timezone.now()
        cart = ShoppingCart(self.request)
        cart_total = cart.get_total_price()
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

    # ------------------- Discount Logic -------------------
    def apply_discount(self):
        discount = Decimal("0.00")
        message = "Coupon applied."
        cart = ShoppingCart(self.request)
        cart_total = cart.get_total_price()

        if self.discount_type == self.DiscountType.PERCENTAGE:
            for item in cart:
                if self.applicable_products.exists() and item.product not in self.applicable_products.all():
                    continue
                if self.applicable_categories.exists() and item.product.category not in self.applicable_categories.all():
                    continue
                if self.applicable_brands.exists() and item.product.brand not in self.applicable_brands.all():
                    continue
                item_discount = (item.price * self.value / Decimal("100"))
                discount += item_discount * item.quantity
            message = f"Total price will be discounted by {self.value}%"

        elif self.discount_type == self.DiscountType.FIXED_AMOUNT:
            discount = Decimal(self.value)
            message = f"Total price will be discounted by {self.value}"

        elif self.discount_type == self.DiscountType.FREE_SHIPPING:
            discount = Decimal("0.00")
            message = "Free shipping will be applied to your order."

        elif self.discount_type == self.DiscountType.BOGO:
            for item in cart:
                if self.applicable_products.exists() and item.product not in self.applicable_products.all():
                    continue
                free_qty = item.quantity // 2
                discount += free_qty * item.price
            message = "Buy one get one offer applied."

        elif self.discount_type == self.DiscountType.GIFT:
            discount = Decimal(self.gift_balance or 0)
            message = f"Gift voucher applied: {discount}"

        elif self.discount_type == self.DiscountType.TIERED:
            tiers = [
                (Decimal("1000.00"), Decimal("20")),  # 20% for >= 1000
                (Decimal("500.00"), Decimal("10")),   # 10% for >= 500
            ]
            applied = False
            for min_amount, percent in tiers:
                if cart_total >= min_amount:
                    discount = cart_total * percent / Decimal("100")
                    message = f"Tiered discount: {percent}% off for orders above {min_amount}"
                    applied = True
                    break
            if not applied:
                message = "No tiered discount applied."

        return discount, message


class CouponRedemption(models.Model):
    """
    علشان نسجل كل مرة الكوبون اتستخدم
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE,related_name="redemptions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey("order.Order", on_delete=models.SET_NULL, null=True, blank=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} used by {self.user}"
