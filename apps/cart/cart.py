from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.store.models import Product

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.session_id = settings.CART_SESSION_ID
        self.cart = self._get_or_create_cart()

    def _get_or_create_cart(self):
        cache_key = self._cache_key()
        cart = cache.get(cache_key)
        if cart is None:
            cart = self.session.get(self.session_id, {})
            if not isinstance(cart, dict):
                cart = {}
            cache.set(cache_key, cart, timeout=3600)
        return cart

    def _cache_key(self):
        if self.request.user.is_authenticated:
            return f"cart_user_{self.request.user.id}"
        return f"cart_session_{self.session.session_key}"

    def add(self, product: Product, quantity: int = 1):
        if not product.pk:
            return
        if quantity <= 0:
            self.remove(product)
            return

        slug = str(product.slug)
        price = Decimal(product.compare_at_price)
        item = self.cart.get(slug, {
            "quantity": 0,
            "price": str(price),
            "tax_rate": str(product.tax_rate),
            "added_at": now().isoformat(),
        })

        new_quantity = item["quantity"] + quantity
        if new_quantity > product.stock:
            new_quantity = product.stock

        item["quantity"] = new_quantity
        item["subtotal"] = self.get_subtotal(item)
        self.cart[slug] = item
        self.save()

    def remove(self, product: Product):
        slug = str(product.slug)
        if slug in self.cart:
            del self.cart[slug]
            self.save()

    def decrement(self, product: Product, quantity: int = 1):
        slug = str(product.slug)
        if slug in self.cart:
            self.cart[slug]["quantity"] -= quantity
            if self.cart[slug]["quantity"] <= 0:
                self.remove(product)
            else:
                self.cart[slug]["subtotal"] = self.get_subtotal(self.cart[slug])
                self.save()

    def clear(self):
        self.cart = {}
        self.save(clear=True)

    def get_total(self):
        return sum(Decimal(item["subtotal"]) for item in self.cart.values())

    def get_total_tax(self):
        return sum(Decimal(item["price"]) * Decimal(item["tax_rate"]) / 100 * item["quantity"] for item in self.cart.values())

    def get_total_items(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_distinct_items(self):
        return len(self.cart)

    def __iter__(self):
        slugs = list(self.cart.keys())
        products = Product.objects.filter(slug__in=slugs).select_related("category")
        products_map = {str(p.slug): p for p in products}

        for slug, item in self.cart.items():
            product = products_map.get(slug)
            yield {
                "product": product,
                "tax_rate": Decimal(item["tax_rate"]),
                "quantity": item["quantity"],
                "price": Decimal(item["price"]),
                "added_at": item.get("added_at"),
                "subtotal": self.get_subtotal(item),
            }

    def save(self, clear: bool = False):
        self.session[self.session_id] = self.cart
        self.session.modified = True
        cache_key = self._cache_key()
        if clear:
            cache.delete(cache_key)
        else:
            cache.set(cache_key, self.cart, timeout=3600)

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


    def get_subtotal(self, item):
        price = Decimal(item["price"])
        tax_rate = Decimal(item["tax_rate"])
        quantity = item["quantity"]
        return (price + price * tax_rate / 100) * quantity
