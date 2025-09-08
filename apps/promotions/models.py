# from celery import uuid
from django.forms import ValidationError
from django.utils import timezone
from django.db import models
from core.utils import MAX_INT
from uuid import uuid4
from decimal import Decimal

class PromotionType(models.TextChoices):
    # NEW_CUSTOMER = 'new_customer', 'New Customer Discount'
    # BULK = 'bulk', 'Bulk Discount' # In handle it in Collection Model
    # CART = 'cart', 'Cart/Order Discount'
    # CATEGORY = 'category', 'Category Discount'
    # BRAND = 'brand', 'Brand Discount'
    # FLASH_SALE = 'flash_sale', 'Time-limited/Flash Sale'
    # SEASONAL = 'seasonal', 'Seasonal Promotion'
    # CLEARANCE = 'clearance', 'Clearance Sale'
    # RETURNING_CUSTOMER = 'returning_customer', 'Returning Customer Discount'
    # COUPON = 'coupon', 'Coupon/Promo Code'
    # EMPLOYEE = 'employee', 'Employee Discount'
    # MEMBERSHIP = 'membership', 'Membership Discount'
    # SPEND_X = 'spend_x', 'Spend X Get Discount'
    # SECOND_ITEM = 'second_item', 'Second Item Discount'
    pass


class BQGPromotion(models.Model):  # handled in cart
    quantity_to_buy = models.PositiveIntegerField(help_text="Quantity required to activate promotion")
    gift = models.ForeignKey("store.Product", on_delete=models.CASCADE, related_name="bqg_promotions")
    gift_quantity = models.PositiveIntegerField(help_text="Quantity of free gift")

    percentage_amount = models.DecimalField(help_text="Percentage discount on gift (0-100)",max_digits=5,decimal_places=2,null=True,blank=True)
    fixed_amount = models.DecimalField(help_text="Fixed discount amount applied to total gift price",max_digits=10,decimal_places=2,null=True,blank=True,)

    def is_valid(self, bought_qty: int) -> bool:
        """Check if promotion is applicable based on purchased quantity and stock."""
        if bought_qty < self.quantity_to_buy:
            return False

        if self.gift.stock_quantity < self.gift_quantity:
            return False

        return True

    @property
    def base_gift_price(self) -> Decimal:
        """Price of gift items before applying discounts."""
        return Decimal(self.gift.final_price) * self.gift_quantity

    @property
    def discounted_gift_price(self) -> Decimal:
        """Final price of gift items after applying promotion discounts."""
        price = self.base_gift_price

        if self.percentage_amount:
            price -= price * (Decimal(self.percentage_amount) / 100)

        if self.fixed_amount:
            price -= Decimal(self.fixed_amount)

        return max(price, Decimal("0"))

    @property
    def discounted_gift_price_with_tax(self) -> Decimal:
        """Gift price after discount + tax."""
        price = self.discounted_gift_price
        # tax_rate = Decimal(self.gift.tax_rate or 0)
        return price #+ (price * tax_rate / 100)

    @property
    def total_gift_price(self) -> Decimal:
        """Total price of all gift items after applying discounts and tax."""
        return self.discounted_gift_price_with_tax * self.gift_quantity

    def bqq_summary(self):
        """Return a summary of the BQG promotion."""
        return {
            "gift": str(self.gift),
            "quantity_to_buy": self.quantity_to_buy,
            "gift_quantity": self.gift_quantity,
            "total_gift_price": Decimal(self.total_gift_price),
        }

    def __str__(self):
        return f"BQGPromotion(gift={self.gift}, quantity_to_buy={self.quantity_to_buy}, gift_quantity={self.gift_quantity})"

class ShippingPromotion(models.Model):
    shipping_discount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage shipping discount amount")
    min_purchase_amount = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum purchase amount to qualify for free shipping")

    def clean(self):
        if self.shipping_discount < 0 or self.shipping_discount > 100:
            raise ValidationError("Shipping discount must be between 0 and 100.")

class Promotion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    percentage_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    bqg = models.OneToOneField(
        "BQGPromotion", on_delete=models.CASCADE,
        null=True, blank=True, related_name="promotion"
    )

    shipping = models.OneToOneField(
        ShippingPromotion, on_delete=models.CASCADE,
        null=True, blank=True, related_name="promotion"
    )

    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True, default=MAX_INT)
    usage_count = models.PositiveIntegerField(default=0)

    def is_valid(self) -> bool:
        """Check if promotion is active, within date range, and under usage limit."""
        return (
            self.is_active
            and self.start_date <= timezone.now() <= self.end_date
            and self.usage_count < self.usage_limit
        )

    def handle_amount_discount(self, price: Decimal) -> Decimal:
        """
        Apply percentage or fixed amount discount to the given price.
        Returns the discounted price, ensuring it is not negative.
        """
        if not self.is_valid():
            return Decimal(price)

        discounted_price = Decimal(price)

        if self.percentage_amount is not None:
            discounted_price -= discounted_price * (Decimal(self.percentage_amount) / Decimal("100"))

        elif self.fixed_amount is not None:
            discounted_price -= Decimal(self.fixed_amount)

        return max(discounted_price, Decimal("0"))

    def get_promotion(self):
        """
        Return the underlying promotion object (e.g., BQGPromotion).
        If no subtype exists, return None.
        """
        if self.bqg:
            return self.bqg

        if self.shipping:
            return self.shipping

        # Add other promotion types here as needed
        return None

    #make if instance has fixed discount cant have percentage discount and vice versa
    def clean(self):
        if self.percentage_amount and self.fixed_amount:
            raise ValidationError("Cannot have both percentage and fixed amount discounts.")

        if self.percentage_amount is not None and self.percentage_amount < 0:
            raise ValidationError("Percentage amount must be positive.")
        if self.fixed_amount is not None and self.fixed_amount < 0:
            raise ValidationError("Fixed amount must be positive.")
        if self.bqg is None and not (self.percentage_amount or self.fixed_amount or self.shipping):
            raise ValidationError("Either BQG promotion or a discount amount must be set.")
        if self.bqg and (self.percentage_amount or self.fixed_amount or self.shipping):
            raise ValidationError("BQG promotion cannot have additional discount amounts.")
        if self.shipping and (self.percentage_amount or self.fixed_amount or self.bqg):
            raise ValidationError("Shipping promotion cannot have additional discount amounts.")

    def __str__(self):
        if self.bqg:
            return str(self.bqg)

        if self.percentage_amount:
            return f"Promotion({self.percentage_amount}% off)"

        if self.fixed_amount:
            return f"Promotion(${self.fixed_amount} off)"

        if self.shipping:
            return str(self.shipping)
        
    
    