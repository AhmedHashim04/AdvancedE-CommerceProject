from django.utils import timezone
from django.db import models
from core.utils import MAX_INT
from apps.store.models import Product

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


    FREE_SHIPPING = 'free_shipping', 'Free Shipping'

class BQGPromotion(models.Model): # handeled in cart
    quantity_to_buy = models.PositiveIntegerField(help_text="quantity to buy")
    gift = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bqg_promotions")
    gift_quantity = models.PositiveIntegerField(help_text="quantity to get")

    percentage_amount = models.DecimalField(help_text="precentage discount in new quantity only",
                            max_digits=5, decimal_places=2, null=True, blank=True, default=100)

    fixed_amount = models.DecimalField(help_text="fixed discount in new quantity only",
                            max_digits=10, decimal_places=2, null=True, blank=True)


    def handle_bqg(self,product,cart):
        if product.quantity < self.quantity_to_buy:
            return

        if self.gift.stock_quantity < self.gift_quantity:
            self.gift.promotion = None
            return

        if self.percentage_amount:
            discount = self.gift.base_price * (self.percentage_amount / 100)

        if self.fixed_amount:
            discount += self.fixed_amount

        cart.add(self.gift, self.gift_quantity, discount=discount)


class Promotion(models.Model):
    percentage_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    bogo = models.OneToOneField(BQGPromotion, on_delete=models.CASCADE, null=True, blank=True, related_name="promotion")

    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True, default=MAX_INT)
    usage_count = models.PositiveIntegerField(default=0)

    @property
    def is_valid(self):
        return self.is_active and self.start_date <= timezone.now() <= self.end_date and self.usage_count < self.usage_limit

    def handle_amount_discount(self, price):
        if self.percentage_amount:
            price -= price * (self.percentage_amount / 100)

        if self.fixed_amount:
            price -= self.fixed_amount

        return max(price, 0)