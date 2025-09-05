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

    def get_promo(self, product, quantity):
        promo = product.promotion.get_promotion()
        if promo and promo.is_valid(quantity):
            return promo
        return None

    def disactive_promotion(self, item, promotion: Promotion):
        item["promotion"] = None
        item["subtotal"] = self.get_subtotal(item, promotion)
        self.save()

    def active_promotion(self, item, promotion: Promotion):
        if promotion.is_valid():
            item["promotion"] = promotion
        item["subtotal"] = self.get_subtotal(item)
        self.save()

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
                "price": str(Decimal(product.final_price)),
                "quantity": min(quantity, product.stock),
                "tax_rate": str(Decimal(product.tax_rate)),
                "promotion": str(promo) if promo else None,
                "added_at": timezone.now().isoformat(),
            }
            cart_item = self.cart[slug]
            self.cart[slug].update({"subtotal": self.get_subtotal(cart_item)})

        self.save()

    def get_subtotal(self, item):
        base_price = Decimal(item["price"]) * item["quantity"] 

        if item["promotion"] :
            discounted_price = item["promotion"].handle_amount_discount(base_price)
        else:
            discounted_price = base_price

        total_with_tax = discounted_price + discounted_price * Decimal(item["tax_rate"]) / 100
        return str(total_with_tax)

    def get_cart_summary(self):
        total_items = sum(item["quantity"] for item in self.cart.values())
        total_price = self.get_total_price()
        return {
            "total_items": total_items,
            "total_price": str(total_price),
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
        self.session.modified = True

    def get_total_price(self):
        prices = [item["subtotal"] for item in self.cart]
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

            if new_quantity > product.stock:
                new_quantity = product.stock

            if product_slug in merged_cart:
                merged_cart[product_slug]["quantity"] = new_quantity

            item_copy = item.copy()
            merged_cart[product_slug] = item_copy
            added_count += 1

        cache.set(user_cart_key, merged_cart, timeout=3600)
        cache.delete(session_cart_key)
        return added_count
