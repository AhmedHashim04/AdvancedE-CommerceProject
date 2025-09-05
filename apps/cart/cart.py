from django.conf import settings
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

    def disactive_promotion(self, item):
        item["promotion"] = None
        item["subtotal"] = str(
            (Decimal(item["price"]) + Decimal(item["price"]) * Decimal(item["tax_rate"]) / 100) 
            * item["quantity"]
        )
        self.save()

    def active_promotion(self, item, promotion: Promotion):
        item["promotion"] = str(promotion.id)
        item["subtotal"] = self.get_subtotal(item, promotion)
        self.save()

    def get_promo(self, product, quantity):
        promo = product.promotion.get_promotion()
        if promo and promo.is_valid(quantity):
            return promo
        return None

    def update(self, product, item, quantity):
        current_qty = item["quantity"]
        max_addable = product.stock - current_qty
        if max_addable <= 0:
            return
        add_qty = min(quantity, max_addable)
        item["quantity"] = current_qty + add_qty
        if not item.get("promotion"):
            promo = self.get_promo(product, item["quantity"])
            if promo:
                self.active_promotion(item, promo)
        self.save()

    def get_subtotal(self, item, promotion=None):
        base_price = Decimal(item["price"]) * item["quantity"] 

        if promotion:
            discounted_price = promotion.handle_amount_discount(base_price)
        else:
            discounted_price = base_price

        total_with_tax = discounted_price + discounted_price * Decimal(item["tax_rate"]) / 100
        return str(total_with_tax)

    def add(self, product, quantity: int = 1) -> None:
        if not product.pk:
            return

        if quantity <= 0:
            self.remove(product)
            return

        slug = str(product.slug)
        item = self.cart.get(slug)
        promo = self.get_promo(product, quantity)

        if item:
            self.update(product, item, quantity)
        else:
            self.cart[slug] = {
                "quantity": min(quantity, product.stock),
                "price": str(Decimal(product.final_price)),
                "tax_rate": str(Decimal(product.tax_rate)),
                "promotion": str(promo.id) if promo else None,
                "added_at": timezone.now().isoformat(),
                "subtotal": self.get_subtotal({"price": product.final_price, "quantity": quantity, "tax_rate": product.tax_rate}, promo),
            }
        self.save()

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
        self.session.modified = True

    def get_total_price(self):
        pass

    def __len__(self):
        pass

    def __iter__(self):
        pass


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
            if product_slug in merged_cart:
                new_quantity += merged_cart[product_slug]["quantity"]

            if new_quantity > product.stock:
                new_quantity = product.stock

            item_copy = item.copy()
            item_copy["quantity"] = new_quantity
            item_copy["subtotal"] = str((Decimal(item_copy["price"]) + Decimal(item_copy["price"]) * Decimal(item_copy["tax_rate"]) / 100) * new_quantity)
            merged_cart[product_slug] = item_copy
            added_count += 1

        cache.set(user_cart_key, merged_cart, timeout=3600)
        cache.delete(session_cart_key)
        return added_count
