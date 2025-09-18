
from django.core.cache import cache
from decimal import Decimal
from django.utils import timezone
from apps.store.models import Product
from apps.shipping.models import Address
from apps.promotions.models import Promotion


class ShoppingCart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.cart = self._get_cart_items()
        self.shipping = self._get_shipping()

    def _cache_key_cart(self):
        if self.request.user.is_authenticated:
            return f"cart_user_{self.request.user.id}"
        return f"cart_session_{self.session.session_key}"
    
    def _cache_key_shipping(self):
        if self.request.user.is_authenticated:
            return f"shipping_user_{self.request.user.id}"
        return f"shipping_session_{self.session.session_key}"

    def _get_cart_items(self):
        cache_key_cart = self._cache_key_cart()
        cart = cache.get(cache_key_cart)
        if cart is None:
            cart = self.session.get("cart", {})
            if not isinstance(cart, dict):
                cart = {}
            cache.set(cache_key_cart, cart, timeout=3600)
        return cart

    def _get_shipping(self):
        cache_key_shipping = self._cache_key_shipping()
        shipping = cache.get(cache_key_shipping)
        if shipping is None:
            shipping = self.session.get("shipping", {})
            if not isinstance(shipping, dict):
                shipping = {}
            cache.set(cache_key_shipping, shipping, timeout=3600)
        return shipping


    def save(self):
        cache_key_cart = self._cache_key_cart()
        cache_key_shipping = self._cache_key_shipping()
        cache.set(cache_key_cart, self.cart, timeout=3600)
        cache.set(cache_key_shipping, self.shipping, timeout=3600)
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

    def get_promotion(self, product, quantity):
        promo = getattr(product, "promotion", None)
        if not (promo and promo.is_valid()):
            return None
        summary = promo.summary(quantity)
        return summary

    def iterate_cart_items_to_add_shipping_costs_based_on_new_address(self, address=None):
        """
        Updates shipping costs for all cart items based on the provided address or the user's default address.
        """
        governorate = None
        if address and hasattr(address, "governorate"):
            governorate = address.governorate
        elif self.request.user.is_authenticated:
            default_address = Address.objects.filter(user=self.request.user, is_default=True).first()
            if default_address:
                governorate = default_address.governorate
        if not governorate:
            self.shipping["address"] = "No Address yet"
            self.save()
            return
        for slug, item in self.cart.items():
            try:
                product = Product.objects.get(slug=slug)
            except Product.DoesNotExist:
                continue
            quantity = int(item.get("quantity", 1))
            self.calculate_shipping_cost(product, quantity, governorate)
        self.calculate_total_shipping_cost()
        self.save()

    def calculate_shipping_cost(self, product, quantity, governorate=None):
        """
        Calculates and updates the shipping cost for a product and quantity to a specific governorate.
        """
        if governorate is None:
            self.shipping["address"] = "No Address yet"
            return
        plan = product.shipping_plan(governorate)
        weight = Decimal(product.weight or 0)
        kilos = weight * quantity
        if plan not in self.shipping:
            self.shipping[plan] = {}
        self.shipping[plan]["base_price"] = str(getattr(plan, "base_price", "0.00"))
        self.shipping[plan][str(product.slug)] = float(kilos)  # Store as float for summing
        self.save()

    def calculate_total_shipping_cost(self):
        """
        Calculates the total shipping cost for all shipping plans in the cart.
        """
        total_shipping_cost = Decimal("0.00")
        if self.shipping.get("address") == "No Address yet":
            return total_shipping_cost
        for plan, details in self.shipping.items():
            if plan == "address":
                return None
            total_plan_weight = sum(
                Decimal(str(weight)) for key, weight in details.items() if key != "base_price"
            )
            base_price = Decimal(details.get("base_price", "0.00"))
            # Assume plan.shipping_plan_weight_cost exists and returns Decimal
            weight_cost = plan.shipping_plan_weight_cost(total_plan_weight) if hasattr(plan, "shipping_plan_weight_cost") else Decimal("0.00")
            total_shipping_cost += base_price + weight_cost
        return total_shipping_cost
    
    def add(self, product, quantity: int = 1) -> None:
        """
        Adds a product to the cart, applies promotion if available, and updates shipping.
        """
        if not self._check_addable(product, quantity):
            return
        slug = str(product.slug)
        promo = self.get_promotion(product, quantity)
        self.cart[slug] = {
            "base_price": str(product.base_price),
            "price": str(product.final_price),
            "quantity": quantity,
        }
        if promo:
            self.cart[slug]["promotion"] = promo
        self.cart[slug]["subtotal"] = str(self.get_subtotal(self.cart[slug], promo))
        governorate = None
        if self.request.user.is_authenticated:
            default_address = Address.objects.filter(user=self.request.user, is_default=True).first()
            if default_address:
                governorate = default_address.governorate
        if governorate:
            self.calculate_shipping_cost(product, quantity, governorate)
        else:
            self.shipping["address"] = "No Address yet"
        self.save()

    def get_subtotal(self, item, promotion=None):

        quantity = int(item.get("quantity", 1))
        price = Decimal(item.get("price", "0"))
        subtotal = price * quantity
        # Handle promotion logic
        if promotion:
            # Ensure promotion is a dict before accessing .get
            if isinstance(promotion, dict) and promotion.get("type") == "BQG":
                # Buy X Get Y logic
                gift_price = Decimal(promotion.get("total_gift_price", "0"))
                subtotal += gift_price


        return subtotal
    
    def get_cart_summary(self,address=None):
        response = {}

        total_items = sum(int(item["quantity"]) for item in self.cart.values())
        total_price = self.get_total_price()
        response.update({
            "total_items": total_items,
            "total_price": str(total_price),
        })

        if address:
            self.iterate_cart_items_to_add_shipping_costs_based_on_new_address(address)
            shipping_cost = self.calculate_total_shipping_cost()
            response.update({
                "shipping_cost": str(shipping_cost),
            })
            response.update({
                "grand_total": str(total_price + shipping_cost),
            })
        return response



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
        cache_key_cart = self._cache_key_cart()
        cache.delete(cache_key_cart)
        self.session["cart"] = {}
        self.shipping = {}
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

        session_shipping_key = f"shipping_session_{old_session_key}"
        user_shipping_key = f"shipping_user_{user.id}"

        session_cart = cache.get(session_cart_key, {})
        user_cart = cache.get(user_cart_key, {})
        session_shipping = cache.get(session_shipping_key, {})
        user_shipping = cache.get(user_shipping_key, {})

        merged_cart = user_cart.copy()
        added_count = 0

        # Merge shipping information
        for key, value in session_shipping.items():
            if key not in user_shipping:
                user_shipping[key] = value
        cache.set(user_shipping_key, user_shipping, timeout=3600)

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
        slug = str(product.slug)
        item = self.cart.get(slug)
        if item is None:
            return
        if "promotion" in item and isinstance(item["promotion"], dict) and item["promotion"].get("type") == "BQG":
            item["promotion"] = "disactivated"
            self.cart[slug].update({"subtotal": str(self.get_subtotal(self.cart[slug]))})
            self.save()

    def reactivate_promotion(self, product):
        slug = str(product.slug)
        item = self.cart.get(slug)
        if item is None:
            return
        if item.get("promotion") == "disactivated":
            quantity = int(item.get("quantity", 1))
            if promo := self.get_promotion(product, quantity):
                self.cart[slug].update({"promotion": promo})
                self.cart[slug].update({"subtotal": str(self.get_subtotal(self.cart[slug], promo))})
                self.save()