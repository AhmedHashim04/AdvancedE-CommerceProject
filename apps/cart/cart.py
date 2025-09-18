
from django.core.cache import cache
from decimal import Decimal
from django.utils import timezone
from apps.store.models import Product
from apps.shipping.models import Address


class ShoppingCart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.cart = self._get_cart_items()
        self.shipping = self._get_shipping()

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

    def _get_shipping(self):
        shipping = self.session.get("shipping", {})
        if not isinstance(shipping, dict):
            shipping = {}
        return shipping

    def save(self):
        cache_key = self._cache_key()
        cache.set(cache_key, self.cart, timeout=3600)
        self.session["cart"] = self.cart
        self.session["shipping"] = self.shipping
        self.session.modified = True
    
    def _check_addable(self, product, quantity):
        if not product.pk:
            return
        if quantity <= 0:
            return False
        if product.stock_quantity < quantity:
            return False
        return True


    def iterate_cart_items_to_add_shipping_costs_based_on_new_address(self):
        for slug, item in self.cart.items():
            try:
                product = Product.objects.get(slug=slug)
            except Product.DoesNotExist:
                continue
            quantity = int(item.get("quantity", 1))
            governorate = Address.objects.filter(user=self.request.user, is_default=True).first().governorate
            if self.request.user.is_authenticated and governorate:
                self.calculate_shipping_cost(product, quantity, governorate)
        self.calculate_total_shipping_cost()
        self.save()



    def calculate_shipping_cost(self, product, quantity, governorate = None):

        if governorate is None:
            return  self.shipping.update({"address": "No Address yet"})
        
        plan = product.shipping_plan(governorate)
        weight = product.weight or 0
        kilos = weight * quantity
        if plan not in self.shipping:
            self.shipping[plan] = {}
        self.shipping[plan]["base_price"] = str(getattr(plan, "base_price", "0.00"))
        self.shipping[plan][str(product.slug)] = kilos
        
    def calculate_total_shipping_cost(self):
        total_shipping_cost = Decimal("0.00")
        total_weight = Decimal("0.00")
        if self.shipping["address"] == "No Address yet":
            return total_shipping_cost
        
        for plan, details in self.shipping.items():
            total_plan_weight = sum(
                weight for key, weight in details.items() if key != "base_price"
            )
            total_shipping_cost += Decimal(details.get("base_price", "0.00"))
            total_weight += plan.shipping_plan_weight_cost(total_plan_weight)
            total_shipping_cost += total_weight
        return total_shipping_cost

    def add(self, product, quantity: int = 1) -> None:
        if not self._check_addable(product, quantity): return

        slug = str(product.slug)

        self.cart[slug] = {
            "base_price": str(product.base_price),
            "price": str(product.final_price),
            "quantity": quantity,
            }

        governorate = Address.objects.filter(user=self.request.user, is_default=True).first().governorate
        
        if self.request.user.is_authenticated and governorate:
                self.calculate_shipping_cost(product, quantity, governorate)
        self.save()

    def get_subtotal(self, item):

        quantity = int(item.get("quantity", 1))
        price = Decimal(item.get("price", "0"))
        subtotal = price * quantity
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
        plan = product.shipping_plan
        if plan in self.shipping and slug in self.shipping[plan]:
            self.shipping[plan].pop(slug, None)
            if all(k == "base_price" for k in self.shipping[plan].keys()):
                self.shipping.pop(plan, None)
        if slug in self.cart:
            del self.cart[slug]
            self.save()
 
    def clear(self):
        self.cart = {}
        cache_key = self._cache_key()
        cache.delete(cache_key)
        self.session["cart"] = {}
        # self.shipping = {}
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
