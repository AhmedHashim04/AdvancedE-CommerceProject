
from django.core.cache import cache
from decimal import Decimal
from django.utils import timezone
from apps.store.models import Product
from apps.promotions.models import Promotion

class ShoppingCart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.cart = self._get_cart_items()
        self.shipping = {}

    def _cache_key(self):
        if self.request.user.is_authenticated:
            return f"cart_user_{self.request.user.id}"
        return f"cart_session_{self.session.session_key}"

    def _get_cart_items(self):
        cache_key = self._cache_key()
        cart = cache.get(cache_key)
        if cart is None:
            cart = self.session.get("cart", {})
            if not isinstance(cart, dict):
                cart = {}
            cache.set(cache_key, cart, timeout=3600)
        return cart

    def save(self):
        cache_key = self._cache_key()
        cache.set(cache_key, self.cart, timeout=3600)
        self.session["cart"] = self.cart
        self.session.modified = True
    
    def _check_addable(self, product, quantity):
        if not product.pk:
            return
        if quantity <= 0:
            return False
        if product.stock_quantity < quantity:
            return False
        return True


    def get_promotion(self, product, quantity):
        promo = product.promotion
        if not (promo and promo.is_valid()):
            return None
        if promo.type in ("fixed", "percentage"):
            return str(promo)
        
        if promo.type == "BQG":
            return promo.summary(quantity)

    def calculate_shipping_cost(self, product, quantity):
        plan = product.shipping_plan
        weight = product.weight or 0
        kilos = weight * quantity
        if plan not in self.shipping:
            self.shipping[plan] = {}
        self.shipping[plan]["base_price"] = str(getattr(plan, "base_price", "0.00"))
        self.shipping[plan][str(product.slug)] = kilos
        
    def calculate_total_shipping_cost(self):
        total_shipping_cost = Decimal("0.00")
        total_weight = Decimal("0.00")
        for plan, details in self.shipping.items():
            total_plan_weight = sum(
                weight for key, weight in details.items() if key != "base_price"
            )
            total_shipping_cost += Decimal(details.get("base_price", "0.00"))
            total_weight += plan.shipping_plan_weight_cost(total_plan_weight)
            total_shipping_cost += total_weight
        return total_shipping_cost

    def add(self, product, quantity: int = 1) -> None:
        if not self._check_addable(product, quantity):return

        slug = str(product.slug)

        self.cart[slug] = {
            "base_price": str(product.base_price),
            "price": str(product.final_price),
            "quantity": str(min(quantity, product.stock_quantity)),
            "added_at": timezone.now().isoformat(),
        }

        self.calculate_shipping_cost(product, quantity)

        if promo := self.get_promotion(product, quantity):
            self.cart[slug].update({"promotion": promo})
            self.cart[slug].update({"subtotal": str(self.get_subtotal(self.cart[slug], promo))})
        else:
            self.cart[slug].update({"subtotal": str(self.get_subtotal(self.cart[slug]))})
        self.save()

    def get_subtotal(self, item, promotion=None):

        quantity = int(item.get("quantity", 1))
        price = Decimal(item.get("price", "0"))
        subtotal = price * quantity

        # Handle promotion logic
        if promotion:
            # If promo is a string, try to parse if possible
            if isinstance(promotion, dict) and promotion.get("type") == "BQG":
                # Buy X Get Y logic
                gift_price = Decimal(promotion.get("total_gift_price", "0"))
                subtotal += gift_price

        return subtotal
    
    def get_cart_summary(self):
        total_items = sum(int(item["quantity"]) for item in self.cart.values())
        total_price = self.get_total_price()
        shipping_cost = self.calculate_total_shipping_cost()
        return {
            "total_items": total_items,
            "total_price": str(total_price),
            "shipping_cost": str(shipping_cost),
        }


    def remove(self, product: Product):
        slug = str(product.slug)
        if slug in self.cart:
            del self.cart[slug]
            self.save()
 
    def clear(self):
        self.cart = {}
        cache_key = self._cache_key()
        cache.delete(cache_key)
        self.session["cart"] = {}
        self.save()


    def get_total_price(self):
        prices = [Decimal(item["subtotal"]) for item in self.cart.values()]
        return sum(prices)
    
    def __len__(self):
        count = 0
        for _ in self.cart:
            count += 1
        return count
    
    def __iter__(self):
        for item in self.cart.values():
            yield item

    @staticmethod
    def merge_on_login(user, old_session_key) -> int:
        session_cart_key = f"cart_session_{old_session_key}"
        user_cart_key = f"cart_user_{user.id}"

        session_cart = cache.get(session_cart_key, {})
        user_cart = cache.get(user_cart_key, {})

        merged_cart = user_cart.copy()
        added_count = 0

        for product_slug, item in session_cart.items():
            try:
                product = Product.objects.get(slug=product_slug)
            except Product.DoesNotExist:
                continue

            new_quantity = item["quantity"]

            if new_quantity > product.stock_quantity:
                new_quantity = product.stock_quantity

            if product_slug in merged_cart:
                merged_cart[product_slug]["quantity"] = new_quantity

            item_copy = item.copy()
            merged_cart[product_slug] = item_copy
            added_count += 1

        cache.set(user_cart_key, merged_cart, timeout=3600)
        cache.delete(session_cart_key)
        return added_count

    def deactive_promotion(self, product):
        item = self.cart.get(str(product.slug))
        if "promotion" in item.keys() and item["promotion"]["type"] in ["BQG"]:
            item["promotion"] = "disactivated"
            
        self.cart[product.slug].update({"subtotal": str(self.get_subtotal(self.cart[product.slug]))})
        self.save()


    def reactive_promotion(self, product):
        item = self.cart.get(str(product.slug))
        if item is None:
            return
        promo = self.get_promotion(product)
        if promo and promo["type"] in ["BQG"]:
            item["promotion"] = promo
        
        self.cart[product.slug].update({"subtotal": str(self.get_subtotal(self.cart[product.slug], promo))})
        self.save()
