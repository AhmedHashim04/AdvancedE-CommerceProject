from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.sellers.models import Seller

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

class BXGYConfiguration(models.Model):
    pass
    # coupon = models.OneToOneField('Coupon', on_delete=models.CASCADE)
    # buy_product = models.ForeignKey('Product', related_name='bxgy_buy')
    # buy_quantity = models.PositiveIntegerField(_('Buy Quantity'))
    # get_product = models.ForeignKey('Product', related_name='bxgy_get')
    # get_quantity = models.PositiveIntegerField(_('Get Quantity'))

class CouponConfiguration(models.Model):
    pass
    # coupon = models.OneToOneField('Coupon', on_delete=models.CASCADE)
    # usage_limit = models.PositiveIntegerField(null=True, blank=True)
    # usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)
    # minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # allowed_users = models.ManyToManyField(User, blank=True, related_name="coupons", verbose_name=_("Allowed Users"))

    # start_date = models.DateTimeField()
    # end_date = models.DateTimeField()


class Coupon(models.Model):
    pass
    # class DiscountType(models.TextChoices):
    #     PERCENTAGE = "percentage", _("Percentage")
    #     FIXED_AMOUNT = "fixed", _("Fixed Amount")
    #     FREE_SHIPPING = "shipping", _("Free Shipping")

    #     GIFT = "gift", _("Gift with Purchase")
    #     BXGY = "bxgy", _("Buy X Get Y Free (e.g., Buy 5 Get 1 Free)")


    # code = models.CharField(max_length=50, unique=True, db_index=True, help_text=_("Coupon code used by customers"))
    # description = models.TextField(blank=True, null=True)

    # seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="coupons")

    # discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    # value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
    #                             help_text=_("Percentage (0-100) or fixed amount"))


    # is_active = models.BooleanField(default=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # config = models.OneToOneField(CouponConfiguration, on_delete=models.CASCADE, null=True, blank=True)

    # bxgy = models.OneToOneField(BXGYConfiguration, on_delete=models.CASCADE, null=True, blank=True)

    # def __str__(self):
    #     return f"{self.code} ({self.discount_type})"

    # def clean(self):
    #     if self.discount_type == self.DiscountType.PERCENTAGE and self.value > 100:
    #         raise ValidationError("Percentage discount cannot exceed 100%.")
    #     if self.start_date >= self.end_date:
    #         raise ValidationError("End date must be after start date.")

    # # ------------------- Validation -------------------
    # def is_valid(self, cart_total, user=None):
        
    #     now = timezone.now()
    #     if not self.is_active:
    #         return False, "Coupon is not active."
    #     if not (self.start_date <= now <= self.end_date):
    #         return False, "Coupon is not valid at this time."
    #     if self.usage_limit and self.redemptions.count() >= self.usage_limit:
    #         return False, "Coupon usage limit reached."
    #     if user and self.usage_limit_per_user:
    #         if self.redemptions.filter(user=user).count() >= self.usage_limit_per_user:
    #             return False, "You have reached the usage limit for this coupon."
    #     if self.allowed_users.exists() and not self.allowed_users.filter(pk=user.pk).exists():
    #         return False, "This coupon is not allowed for your account."
    #     if self.minimum_order_amount and cart_total is not None and cart_total < self.minimum_order_amount:
    #         return False, f"Order total must be at least {self.minimum_order_amount} to use this coupon."
    #     return True, None

    # def apply_discount(self, cart):
    #     """
    #     Apply discount to the cart based on the coupon type.
    #     Returns:
    #         discount_amount (Decimal), message (str)
    #     """
    #     discount = Decimal("0.00")
    #     message = ""

    #     cart_total = cart.get_total_price()
    #     if cart_total is None:
    #         return discount, "Cart is empty."

    #     if self.discount_type == self.DiscountType.PERCENTAGE:
    #         discount = (cart_total * self.value) / 100
    #         discount = min(discount, cart_total)  # prevent over-discount
    #         cart.apply_discount(discount)
    #         message = f"{self.value}% off applied."

    #     elif self.discount_type == self.DiscountType.FIXED_AMOUNT:
    #         discount = min(self.value, cart_total)
    #         cart.apply_discount(discount)
    #         message = f"{discount} off applied."

    #     elif self.discount_type == self.DiscountType.FREE_SHIPPING:
    #         cart.apply_free_shipping()
    #         message = "Free shipping applied."

    #     elif self.discount_type == self.DiscountType.GIFT:
    #         if not hasattr(self, 'gift_product'):
    #             return discount, "No gift product configured for this coupon."
    #         cart.add_gift(self.gift_product)
    #         message = f"Gift added to your cart: {self.gift_product.name}"

    #     elif self.discount_type == self.DiscountType.BXGY:
    #         if not hasattr(self, 'bxgy_config'):
    #             return discount, "No BXGY configuration for this coupon."
    #         # Example: bxgy_config = {"buy_qty":5, "free_qty":1, "product": ProductInstance}
    #         buy_qty = self.bxgy_config.get("buy_qty", 0)
    #         free_qty = self.bxgy_config.get("free_qty", 0)
    #         product = self.bxgy_config.get("product")
    #         if cart.get_quantity(product) >= buy_qty:
    #             cart.add_free_product(product, free_qty)
    #             message = f"Buy {buy_qty} Get {free_qty} Free applied for {product.name}."
    #         else:
    #             message = f"Buy {buy_qty} of {product.name} to get {free_qty} free."

    #     else:
    #         message = "Invalid coupon type."

    #     return discount, message

class CouponRedemption(models.Model):
    pass
    # coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE,related_name="redemptions")
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    # redeemed_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"{self.coupon.code} used by {self.user}"
    
    # class Meta:
    #     unique_together = ('coupon', 'user', 'order')
