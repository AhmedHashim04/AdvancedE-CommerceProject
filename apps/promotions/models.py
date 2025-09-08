import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import F

# Constant for rounding
DECIMAL_PRECISION = Decimal("0.01")


# --------------------
# Base class
# --------------------
class BasePromotion(models.Model):
    """Abstract base class for all promotions."""

    class Meta:
        abstract = True

    def is_valid(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    def apply_discount(self, price: Decimal) -> Decimal:
        """Default: return unchanged price."""
        return price.quantize(DECIMAL_PRECISION, rounding=ROUND_HALF_UP)

    def summary(self) -> dict:
        raise NotImplementedError


# --------------------
# BQG Promotion
# --------------------
class BQGPromotion(BasePromotion):
    """
    Buy X Get Y Promotion
    Example: Buy 2 phones, get 1 cover with 50% discount
    """
    quantity_to_buy = models.PositiveIntegerField(
        help_text="Quantity required to activate promotion"
    )
    gift = models.ForeignKey(
        "store.Product",
        on_delete=models.CASCADE,
        related_name="bqg_promotions"
    )
    gift_quantity = models.PositiveIntegerField(
        help_text="Quantity of free gift"
    )

    percentage_amount = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Percentage discount on gift (1-100)"
    )
    fixed_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Fixed discount amount applied to total gift price"
    )

    def clean(self):
        # enforce that either percentage or fixed discount (or none), but not both
        if self.percentage_amount and self.fixed_amount:
            raise ValidationError("BQG promotion cannot have both percentage and fixed discount.")

    def is_valid(self, bought_qty: int) -> bool:
        """Check if promotion is applicable based on purchased quantity and stock."""
        return (
            bought_qty >= self.quantity_to_buy
            and self.gift.stock_quantity >= self.gift_quantity
        )

    @property
    def base_gift_price(self) -> Decimal:
        """Price of gift items before applying discounts."""
        return Decimal(self.gift.final_price) * self.gift_quantity

    @property
    def discounted_gift_price(self) -> Decimal:
        """Final price of gift items after applying promotion discounts."""
        price = self.base_gift_price

        if self.percentage_amount is not None:
            price -= price * (self.percentage_amount / Decimal("100"))

        if self.fixed_amount is not None:
            price -= self.fixed_amount

        return max(price, Decimal("0")).quantize(DECIMAL_PRECISION)

    @property
    def discounted_gift_price_with_tax(self) -> Decimal:
        """Gift price after discount + tax"""
        # tax_rate = Decimal(self.gift.tax_rate or 0)
        price = self.discounted_gift_price
        # return price + (price * tax_rate / 100)
        return price

    @property
    def total_gift_price(self) -> Decimal:
        """Total price of all gift items after applying discounts and tax."""
        return self.discounted_gift_price_with_tax

    def summary(self) -> dict:
        return {
            "type": "BQG",
            "gift": str(self.gift),
            "quantity_to_buy": self.quantity_to_buy,
            "gift_quantity": self.gift_quantity,
            "total_gift_price": self.total_gift_price,
        }

    def __str__(self):
        if self.percentage_amount:
            return f"BQG: Buy {self.quantity_to_buy}, Get {self.gift_quantity} x {self.gift} at {self.percentage_amount}% off"
        if self.fixed_amount:
            return f"BQG: Buy {self.quantity_to_buy}, Get {self.gift_quantity} x {self.gift} for ${self.fixed_amount} off"

        return f"BQG: Buy {self.quantity_to_buy}, Get {self.gift_quantity} x {self.gift} "


# # --------------------
# # Shipping Promotion (in Cart Overall)
# # --------------------
# class ShippingPromotion(BasePromotion):
#     """
#     Shipping Promotion
#     Example: Free shipping above $100, or 50% off shipping cost
#     """
#     shipping_discount = models.PositiveIntegerField(
#         null=True, blank=True,
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         help_text="Percentage discount on shipping cost (0-100)"
#     )
#     min_purchase_amount = models.DecimalField(
#         max_digits=10, decimal_places=2,
#         null=True, blank=True,
#         help_text="Minimum purchase amount to qualify"
#     )

#     def clean(self):
#         if self.shipping_discount is None and self.min_purchase_amount is None:
#             raise ValidationError("Either shipping discount or min purchase amount must be set.")

#     def is_valid(self, cart_total: Decimal) -> bool:
#         if self.min_purchase_amount and cart_total < self.min_purchase_amount:
#             return False
#         return True

#     def apply_discount(self, shipping_cost: Decimal) -> Decimal:
#         """Apply shipping discount if available."""
#         if self.shipping_discount:
#             discount_fraction = Decimal(self.shipping_discount) / Decimal("100")
#             shipping_cost -= shipping_cost * discount_fraction
#         return max(shipping_cost, Decimal("0")).quantize(DECIMAL_PRECISION)

#     def summary(self) -> dict:
#         return {
#             "type": "Shipping",
#             "shipping_discount": self.shipping_discount,
#             "min_purchase_amount": self.min_purchase_amount,
#         }

#     def __str__(self):
#         if self.shipping_discount:
#             return f"Shipping {self.shipping_discount}% off"
#         if self.min_purchase_amount:
#             return f"Free shipping over ${self.min_purchase_amount}"
#         return "Shipping Promotion"


# --------------------
# Promotion Main
# --------------------
class PromotionType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage Discount"
    FIXED = "fixed", "Fixed Discount"
    BQG = "bqg", "Buy X Get Y"
    SHIPPING = "shipping", "Free/Discounted Shipping"



class Promotion(BasePromotion):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(
        max_length=20,
        choices=PromotionType.choices,
        help_text="Type of promotion"
    )

    percentage_amount = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Percentage discount (1-100)",
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    fixed_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Fixed discount amount (>0)"
    )

    bqg_promotion = models.OneToOneField(
        BQGPromotion, on_delete=models.CASCADE,
        null=True, blank=True, related_name="promotion"
    )

    # shipping_promotion = models.OneToOneField(
    #     "ShippingPromotion", on_delete=models.CASCADE,
    #     null=True, blank=True, related_name="promotion"
    # )

    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Max number of times this promotion can be used. Null = unlimited."
    )
    usage_count = models.PositiveIntegerField(default=0)

    # --------------------
    # Validation
    # --------------------
    def clean(self):
        self._validate_dates()
        self._validate_discount_logic()


    def _validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date.")

    def _validate_discount_logic(self):
        """Ensure only relevant fields are filled based on type."""

        if self.type == PromotionType.PERCENTAGE:
            if not self.percentage_amount:
                raise ValidationError("Percentage amount is required for percentage promotions.")
            if self.fixed_amount or self.bqg_promotion:  # or self.shipping_promotion:
                raise ValidationError("Percentage promotion cannot have fixed/bqg/shipping fields.")

        elif self.type == PromotionType.FIXED:
            if not self.fixed_amount or self.fixed_amount <= Decimal("0.00"):
                raise ValidationError("Fixed amount must be > 0 for fixed promotions.")
            if self.percentage_amount or self.bqg_promotion:  # or self.shipping_promotion:
                raise ValidationError("Fixed promotion cannot have percentage/bqg/shipping fields.")

        elif self.type == PromotionType.BQG:
            if not self.bqg_promotion:
                raise ValidationError("BQG promotion details are required.")
            if self.percentage_amount or self.fixed_amount:  # or self.shipping_promotion:
                raise ValidationError("BQG promotion cannot have percentage/fixed/shipping fields.")

        # elif self.type == PromotionType.SHIPPING:
        #     if not self.shipping_promotion:
        #         raise ValidationError("Shipping promotion details are required.")
        #     if self.percentage_amount or self.fixed_amount or self.bqg_promotion:
        #         raise ValidationError("Shipping promotion cannot have percentage/fixed/bqg fields.")
        
        else:
            raise ValidationError("Invalid promotion type.")

    # --------------------
    # Logic
    # --------------------
    def is_valid(self) -> bool:
        now = timezone.now()
        return (
            self.is_active
            and self.start_date <= now <= self.end_date
            and (self.usage_limit is None or self.usage_count < self.usage_limit)
        )

    def increment_usage(self):
        """Increase usage safely (atomic update)."""
        if self.usage_limit is not None:
            updated = Promotion.objects.filter(
                id=self.id,
                usage_count__lt=self.usage_limit
            ).update(usage_count=F("usage_count") + 1)
            if not updated:
                raise ValidationError("Usage limit reached.")
        else:
            Promotion.objects.filter(id=self.id).update(usage_count=F("usage_count") + 1)

    def apply_discount(self, price: Decimal) -> Decimal:  # Apply discount if type:(PERCENTAGE, FIXED) to the given price
        """
        it is called from store.models.Product.final_price property
        Apply percentage or fixed amount discount to the given price.
        Returns the discounted price, ensuring it is not negative.
        """
        if not self.is_valid():
            return price.quantize(DECIMAL_PRECISION, rounding=ROUND_HALF_UP)

        discounted_price = price

        if self.type == PromotionType.PERCENTAGE and self.percentage_amount is not None:
            discount_fraction = Decimal(self.percentage_amount) / Decimal("100")
            discounted_price -= discounted_price * discount_fraction

        elif self.type == PromotionType.FIXED and self.fixed_amount is not None:
            discounted_price -= self.fixed_amount

        return max(discounted_price, Decimal("0")).quantize(DECIMAL_PRECISION, rounding=ROUND_HALF_UP)


    def summary(self) -> dict:
        base = {
            "id": str(self.id),
            "type": self.type,
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "usage_limit": self.usage_limit,
        }
        if self.type == PromotionType.PERCENTAGE:
            base["percentage_amount"] = self.percentage_amount
        elif self.type == PromotionType.FIXED:
            base["fixed_amount"] = self.fixed_amount
        elif self.type == PromotionType.BQG and self.bqg_promotion:
            base.update(self.bqg_promotion.summary())
        # elif self.type == PromotionType.SHIPPING and self.shipping_promotion:
        #     base.update(self.shipping_promotion.summary())
        return base

    def __str__(self):
        if self.type == PromotionType.PERCENTAGE:
            return f"{self.percentage_amount}% off"
        elif self.type == PromotionType.FIXED:
            return f"${self.fixed_amount} off"
        elif self.type == PromotionType.BQG:
            return str(self.bqg_promotion)
        elif self.type == PromotionType.SHIPPING:
            return str(self.shipping_promotion)
        return "Promotion (unspecified)"
