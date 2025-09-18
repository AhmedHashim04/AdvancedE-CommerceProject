from django.core.cache import cache
from decimal import Decimal
from django.utils import timezone
from apps.store.models import Product
from apps.shipping.models import Address
from apps.promotions.models import Promotion
from apps.shipping.models import ShippingPlan


class ShoppingCart:
    CACHE_TIMEOUT = 3600

    def __init__(self, request):
        self.request = request
        self.session = request.session
        if not self.session.session_key:
            self.session.save()  # Ensure session key exists
        self.cart = self._get_cart_items()
        self.shipping = self._get_shipping()

    # ======================
    # Cache Key Utilities
    # ======================
    def _cache_key_cart(self):
        if self.request.user.is_authenticated:
            return f"cart_user_{self.request.user.id}"
        return f"cart_session_{self.session.session_key}"

    def _cache_key_shipping(self):
        if self.request.user.is_authenticated:
            return f"shipping_user_{self.request.user.id}"
        return f"shipping_session_{self.session.session_key}"

    # ======================
    # Session & Cache
    # ======================
    def _get_cart_items(self):
        key = self._cache_key_cart()
        cart = cache.get(key)
        if not isinstance(cart, dict):
            cart = self.session.get("cart", {})
            if not isinstance(cart, dict):
                cart = {}
            cache.set(key, cart, self.CACHE_TIMEOUT)
        return cart

    def _get_shipping(self):
        key = self._cache_key_shipping()
        shipping = cache.get(key)
        if not isinstance(shipping, dict):
            shipping = self.session.get("shipping", {})
            if not isinstance(shipping, dict):
                shipping = {}
            cache.set(key, shipping, self.CACHE_TIMEOUT)
        return shipping


    @classmethod
    def _cache_key_cart_for_user(cls, user):
        return f"cart_user_{user.id}"

    @classmethod
    def _cache_key_cart_for_session(cls, session_key):
        return f"cart_session_{session_key}"

    @classmethod
    def _cache_key_shipping_for_user(cls, user):
        return f"shipping_user_{user.id}"

    @classmethod
    def _cache_key_shipping_for_session(cls, session_key):
        return f"shipping_session_{session_key}"

    @classmethod
    def merge_on_login(cls, user, old_session_key) -> int:
        session_cart_key = cls._cache_key_cart_for_session(old_session_key)
        user_cart_key = cls._cache_key_cart_for_user(user)

        session_shipping_key = cls._cache_key_shipping_for_session(old_session_key)
        user_shipping_key = cls._cache_key_shipping_for_user(user)

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
        cache.set(user_shipping_key, user_shipping, timeout=cls.CACHE_TIMEOUT)

        for product_slug, item in session_cart.items():
            try:
                product = Product.objects.get(slug=product_slug)
            except Product.DoesNotExist:
                continue

            new_quantity = item["quantity"]

            if new_quantity > product.stock_quantity:
                new_quantity = product.stock_quantity

            if product_slug in merged_cart:
                # Merge quantities or preserve the higher quantity
                existing_quantity = merged_cart[product_slug].get("quantity", 0)
                merged_quantity = max(existing_quantity, new_quantity)
                item_copy = item.copy()
                item_copy["quantity"] = merged_quantity
                merged_cart[product_slug] = item_copy
            else:
                item_copy = item.copy()
                # Ensure quantity does not exceed stock
                item_copy["quantity"] = min(new_quantity, product.stock_quantity)
                merged_cart[product_slug] = item_copy
            added_count += 1

        cache.set(user_cart_key, merged_cart, timeout=cls.CACHE_TIMEOUT)
        cache.delete(session_cart_key)
        return added_count
    
    def save(self):
        cache.set(self._cache_key_cart(), self.cart, self.CACHE_TIMEOUT)
        cache.set(self._cache_key_shipping(), self.shipping, self.CACHE_TIMEOUT)
        self.session["cart"] = self.cart
        self.session["shipping"] = self.shipping
        self.session.modified = True

  
    # ======================
    # Helpers
    # ======================
    def _check_addable(self, product, quantity):
        return (
            product.pk
            and quantity > 0
            and product.stock_quantity >= quantity
        )

    def _get_governorate(self, address=None):
        if address and getattr(address, "governorate", None):
            return address.governorate
        if self.request.user.is_authenticated:
            default_address = Address.objects.filter(user=self.request.user, is_default=True).first()
            return getattr(default_address, "governorate", None)
        return None
    
    #TODO: get promo weight and details and add it into shipping system   
    def _get_promotion(self, product, quantity):
        promo = getattr(product, "promotion", None)
        if promo and promo.is_valid():
            return promo.summary(quantity)
        return None

    def _recalc_item_subtotal(self, slug, item):
        """Always recalc subtotal from price * qty + promo"""
        qty = int(item.get("quantity", 1))
        price = Decimal(item.get("price", "0"))
        promo = item.get("promotion")
        subtotal = price * qty
        if isinstance(promo, dict) and promo.get("type") == "BQG":
            subtotal += Decimal(promo.get("total_gift_price", "0"))
        self.cart[slug]["subtotal"] = str(subtotal)
        return subtotal

    # ======================
    # Shipping
    # ======================
    def calculate_shipping_cost(self, product, quantity, governorate=None):
        if governorate is None:
            self.shipping["address"] = "No Address yet"
            return
        plan = product.shipping_plan(governorate)
        weight = Decimal(product.weight or 0) * quantity
        if str(plan.id) not in self.shipping:
            self.shipping[str(plan.id)] = {
                "plan_name": getattr(plan, "name", ""),
                "base_price": str(getattr(plan, "base_price", "0.00")),
                "weights": {}
            }
        self.shipping[str(plan.id)]["weights"][str(product.slug)] = float(weight)

    def calculate_total_shipping_cost(self):
        total = Decimal("0.00")
        if self.shipping.get("address") == "No Address yet":
            return total
        
        for plan_id, plan_data in self.shipping.items():
            if not isinstance(plan_data, dict) or "weights" not in plan_data:
                return
            
            total_weight = sum(Decimal(str(w)) for w in plan_data["weights"].values())
            base_price = Decimal(plan_data.get("base_price", "0.00"))
            # Get the ShippingPlan instance
            try:
                plan = ShippingPlan.objects.get(id=plan_id)
                weight_pricing = getattr(plan, "weight_pricing", None)
                if weight_pricing:
                    weight_cost = weight_pricing.shipping_plan_weight_cost(total_weight)
                else:
                    weight_cost = Decimal("0.00")
            except Exception:
                weight_cost = Decimal("0.00")
            total += base_price + Decimal(weight_cost)
        return total
    
    # ======================
    # Cart Actions
    # ======================
    def add(self, product, quantity=1, address=None):
        if not self._check_addable(product, quantity):
            return

        slug = str(product.slug)
        promo = self._get_promotion(product, quantity)

        self.cart[slug] = {
            "base_price": str(product.base_price),
            "price": str(product.final_price),
            "quantity": quantity,
            "promotion": promo or None,
        }
        self._recalc_item_subtotal(slug, self.cart[slug])

        governorate = self._get_governorate(address)
        if governorate:
            self.calculate_shipping_cost(product, quantity, governorate)
        else:
            self.shipping["address"] = "No Address yet"

        self.save()

    def remove(self, product):
        slug = str(product.slug)
        for plan_id, plan_data in list(self.shipping.items()):
            if isinstance(plan_data, dict) and "weights" in plan_data:
                plan_data["weights"].pop(slug, None)
                if not plan_data["weights"]:
                    self.shipping.pop(plan_id, None)
        self.cart.pop(slug, None)
        self.save()

    def clear(self):
        self.cart = {}
        self.shipping = {}
        cache.delete(self._cache_key_cart())
        cache.delete(self._cache_key_shipping())
        self.session["cart"] = {}
        self.session["shipping"] = {}
        self.save()

  # ======================
    # Promotions
    # ======================
    def deactive_promotion(self, product):
        slug = str(product.slug)
        item = self.cart.get(slug)
        if item is None:
            return
        if "promotion" in item and isinstance(item["promotion"], dict) and item["promotion"].get("type") == "BQG":
            item["promotion"] = "disactivated"
            self.cart[slug].update({"subtotal": str(self._recalc_item_subtotal(self.cart[slug]))})
            self.save()

    def reactivate_promotion(self, product):
        slug = str(product.slug)
        item = self.cart.get(slug)
        if item is None:
            return
        if item.get("promotion") == "disactivated":
            quantity = int(item.get("quantity", 1))
            if promo := self._get_promotion(product, quantity):
                self.cart[slug].update({"promotion": promo})
                self.cart[slug].update({"subtotal": str(self._recalc_item_subtotal(self.cart[slug], promo))})
                self.save()
    # ======================
    # Totals & Summary
    # ======================
    def get_total_price(self):
        return sum(
            self._recalc_item_subtotal(slug, item)
            for slug, item in self.cart.items()
        )

    def get_cart_summary(self, address=None):
        total_items = sum(int(item["quantity"]) for item in self.cart.values())
        total_price = self.get_total_price()

        summary = {
            "total_items": total_items,
            "total_price": str(total_price),
        }

        governorate = self._get_governorate(address)
        if governorate:
            for slug, item in self.cart.items():
                product = Product.objects.filter(slug=slug).first()
                if product:
                    self.calculate_shipping_cost(product, int(item["quantity"]), governorate)
            shipping_cost = self.calculate_total_shipping_cost()
            summary["shipping_cost"] = str(shipping_cost)
            summary["grand_total"] = str(total_price + shipping_cost)

        return summary

    # ======================
    # Python Protocols
    # ======================
    def __len__(self):
        return len(self.cart)

    def __iter__(self):
        for slug, item in self.cart.items():
            yield slug, item
