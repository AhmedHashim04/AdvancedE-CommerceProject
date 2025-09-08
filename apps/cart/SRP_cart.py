from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone


class CartStorage:
    def _cache_key(self, request):
        if request.user.is_authenticated:
            return f"cart_user_{request.user.id}"
        return f"cart_session_{request.session.session_key}"

    def load(self, request):
        cache_key = self._cache_key(request)
        cart = cache.get(cache_key)
        if not isinstance(cart, dict):
            cart = request.session.get("cart", {}) or {}
            if not isinstance(cart, dict):
                cart = {}
            cache.set(cache_key, cart, timeout=3600)
        return cart

    def save(self, request, cart):
        cache_key = self._cache_key(request)
        cache.set(cache_key, cart, timeout=3600)
        request.session["cart"] = cart
        request.session.modified = True



class CartCalculator:
    def add_product(self, cart, product, quantity):
        slug = str(product.slug)

        if slug in cart:
            cart[slug]["quantity"] = str(int(cart[slug]["quantity"]) + quantity)
        else:
            cart[slug] = {
                "price": str(product.final_price),
                "quantity": str(min(quantity, product.stock_quantity)),
                "added_at": timezone.now().isoformat(),
            }

        cart[slug]["subtotal"] = self.subtotal(cart[slug], product)
        return cart

    def subtotal(self, item, product):
        base_price = Decimal(item["price"]) * Decimal(item["quantity"])
        return str(base_price)

    def summary(self, cart):
        total_items = sum(int(item["quantity"]) for item in cart.values())
        total_price = sum(Decimal(item["subtotal"]) for item in cart.values())
        return {"total_items": total_items, "total_price": str(total_price)}



class PromotionService:
    def __init__(self, cart={}, product=None, quantity=0):
        self.cart = cart
        self.product = product
        self.quantity = quantity
        self.promo = self.get_promotion()


    def get_promotion(self):
        if promo := getattr(self.product, "promotion", None):
            promo_data = promo.summary(self.quantity)
            return {
                k: (str(v) if isinstance(v, Decimal) else v)
                for k, v in promo_data.items()
            }
        return None

    def apply_promotion(self):
        slug = str(self.product.slug)
        if slug not in self.cart:
            return self.cart
        if self.promo:
            self.cart[slug]["promotion"] = self.promo
        return self.cart

    def deactive_promotion(self):
        slug = str(self.product.slug)
        if slug not in self.cart:
            return self.cart
        self.cart[slug].pop("promotion", None)
        return self.cart

    def reactive_promotion(self):
        slug = str(self.product.slug)
        if slug not in self.cart:
            return self.cart
        if self.promo:
            self.cart[slug]["promotion"] = self.promo
        return self.cart



class CartManager:
    def __init__(self, request,
                 storage: CartStorage,
                 calculator: CartCalculator,
                 promo_service: PromotionService):
        self.request = request
        self.storage = storage
        self.calculator = calculator
        self.promo_service = promo_service
        self.cart = self.storage.load(request)

    def add(self, product, quantity=1):
        self.cart = self.calculator.add_product(self.cart, product, quantity)
        self.cart = self.promo_service.apply_promotion(self.cart, product)
        self.storage.save(self.request, self.cart)

    def remove(self, product):
        slug = str(product.slug)
        if slug in self.cart:
            del self.cart[slug]
        self.storage.save(self.request, self.cart)

    def clear(self):
        self.cart = {}
        self.storage.save(self.request, self.cart)

    def deactive_promotion(self):
        self.cart = self.promo_service.deactive_promotion(self.cart)
        self.storage.save(self.request, self.cart)

    def reactive_promotion(self):
        self.cart = self.promo_service.reactive_promotion(self.cart)
        self.storage.save(self.request, self.cart)

    def summary(self):
        return self.calculator.summary(self.cart)

    def __iter__(self):
        for item in self.cart.values():
            yield item

    def __len__(self):
        return len(self.cart)

