from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", _("Percentage")
        FIXED_AMOUNT = "fixed", _("Fixed Amount")
        FREE_SHIPPING = "shipping", _("Free Shipping")
        BOGO = "bogo", _("Buy One Get One")
        GIFT = "gift", _("Gift Voucher")
        TIERED = "tiered", _("Tiered Discount")

    code = models.CharField(
        max_length=50, unique=True, db_index=True,
        help_text=_("Coupon code used by customers")
    )
    description = models.TextField(blank=True, null=True)

    # نوع الخصم
    discount_type = models.CharField(
        max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE
    )

    # قيمة الخصم (لو نسبة مئوية 0-100, لو مبلغ -> بالعملة)
    value = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Percentage (0-100) or fixed amount")
    )

    # صلاحية
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # مرات الاستخدام
    usage_limit = models.PositiveIntegerField(
        null=True, blank=True,
        help_text=_("Max number of times this coupon can be used in total")
    )
    usage_limit_per_user = models.PositiveIntegerField(
        null=True, blank=True,
        help_text=_("Max number of times this coupon can be used per user")
    )

    # شروط
    minimum_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text=_("Minimum order amount required to apply coupon")
    )
    applicable_categories = models.ManyToManyField(
        "product.Category", blank=True, related_name="coupons"
    )
    applicable_products = models.ManyToManyField(
        "product.Product", blank=True, related_name="coupons"
    )
    applicable_brands = models.ManyToManyField(
        "product.Brand", blank=True, related_name="coupons"
    )

    # كوبونات خاصة بمستخدمين محددين
    allowed_users = models.ManyToManyField(
        User, blank=True, related_name="coupons",
        help_text=_("Restrict coupon to specific users")
    )

    # كوبون هدية (رصيد جاهز)
    gift_balance = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text=_("If this is a gift coupon, this is the balance")
    )

    # حالات عامة
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_type})"

    # --- منطق التحقق والتطبيق ---
    def is_valid(self, user=None, order_total=None, date=None):
        """
        يتحقق إذا الكوبون صالح للاستخدام
        """
        from django.utils import timezone
        now = date or timezone.now()

        if not self.is_active:
            return False
        if not (self.start_date <= now <= self.end_date):
            return False
        if self.usage_limit and self.couponredemption_set.count() >= self.usage_limit:
            return False
        if user and self.usage_limit_per_user:
            if self.couponredemption_set.filter(user=user).count() >= self.usage_limit_per_user:
                return False
        if self.allowed_users.exists() and user not in self.allowed_users.all():
            return False
        if self.minimum_order_amount and order_total and order_total < self.minimum_order_amount:
            return False

        return True


class CouponRedemption(models.Model):
    """
    علشان نسجل كل مرة الكوبون اتستخدم
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey("order.Order", on_delete=models.SET_NULL, null=True, blank=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} used by {self.user}"
