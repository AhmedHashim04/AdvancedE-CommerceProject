from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import now
from apps.store.models import Product
from apps.coupons.models import Coupon


class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.session_id = settings.CART_SESSION_ID # CART_ID
        self.cart = self._get_or_create_cart()

    def _get_or_create_cart(self):
        if self.request.user.is_authenticated:
            cache_key = f"cart_user_{self.request.user.id}"
        else:
            cache_key = f"cart_session_{self.session.session_key}"

        cart = cache.get(cache_key)

        if cart is None:
            cart = self.session.get(self.session_id, {})
            if not isinstance(cart, dict):
                cart = {}

            if self.request.user.is_authenticated:
                cache_key = f"cart_user_{self.request.user.id}"
            else:
                cache_key = f"cart_session_{self.session.session_key}"

            cache.set(cache_key, cart, timeout=3600) # 1 H

        return cart

    def add(self, product: Product, quantity: int = 1):
        if quantity <= 0:
            self.remove(product)
            return

        slug = str(product.slug)
        price = Decimal(product.compare_at_price)
        discount = Decimal(product.compare_at_price - product.price)
        final_price = Decimal(product.price) if product.price > 0 else Decimal(product.compare_at_price)

        item = self.cart.get(slug)

        if not item:
            item = {
                "quantity" : 0,
                "price" : str(price),
                "tax_rate" : str(product.tax_rate),
                "discount" : str(discount),
                "price_after_discount" : str(final_price),
                "added_at" : now().isoformat(),
                "subtotal" : "0",
            }

        item["quantity"] = quantity
        item["subtotal"] = str(final_price * quantity)

        self.cart[slug] = item
        self.save()

    def remove(self, product: Product):
        product_slug = str(product.slug)
        if product_slug in self.cart:
            del self.cart[product_slug]
            self.save()

    def clear(self):
        self.cart = {}
        self.save(clear=True)

    def __iter__(self):
        product_slugs = list(self.cart.keys())
        products = Product.objects.filter(slug__in=product_slugs).select_related(
            "category"
        )
        products_map = {str(p.slug): p for p in products}

        for slug, item in self.cart.items():
            product = products_map.get(slug)
            if not product:
                continue

            discount_amount = Decimal(item["price_after_discount"]) - Decimal(item["discount"]) 

            yield {
                "product" : product,
                "tax_rate" : product.tax_rate,
                "quantity" : item["quantity"],
                "price" : Decimal(item["price"]),
                "discount" : discount_amount,
                "price_after_discount" : Decimal(item["price_after_discount"]),
                "added_at" : item.get("added_at"),
                "subtotal" : Decimal(item["subtotal"]),

            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def save(self, clear: bool = False):
        self.session[self.session_id] = self.cart
        self.session.modified = True

        if self.request.user.is_authenticated:
            cache_key = f"cart_user_{self.request.user.id}"
        else:
            cache_key = f"cart_session_{self.session.session_key}"

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

        for product_id, item in session_cart.items():
            try:
                product = Product.objects.get(slug=product_id)
            except Product.DoesNotExist:
                continue

            new_quantity = item["quantity"]
            if product_id in merged_cart:
                new_quantity += merged_cart[product_id]["quantity"]

            if new_quantity > product.stock:
                continue

            merged_cart[product_id] = item.copy()
            merged_cart[product_id]["quantity"] = new_quantity
            added_count += 1

        cache.set(user_cart_key, merged_cart, timeout=3600)
        cache.delete(session_cart_key)

        return added_count

    def get_total_price(self):
        return sum(
            Decimal(item["price"])*Decimal(item["quantity"]) for item in self.cart.values()
        )

    def get_total_discount(self):
        return sum(
            Decimal(item["discount"])*Decimal(item["quantity"]) for item in self.cart.values()
        )

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_total_discount()

    def get_applied_coupon(self):
        coupon_id = self.session.get('applied_coupon_id')
        if coupon_id:
            try:
                return Coupon.objects.get(id=coupon_id)
            except Coupon.DoesNotExist:
                return None
        return None

    def get_discount_from_coupon(self):
        coupon = self.get_applied_coupon()
        if coupon:
            discount, _ = coupon.apply_discount(self)
            return discount
        return Decimal("0.00")

    def get_final_total(self):
        total_after_discount = self.get_total_price_after_discount()
        coupon_discount = self.get_discount_from_coupon()
        return total_after_discount - coupon_discount


    def get_cart_summary(self):
        total_price_after_discount = self.get_total_price_after_discount()
        coupon_discount = self.get_discount_from_coupon()
        final_total = total_price_after_discount - coupon_discount

        return {
            "total_items": len(self),
            "total_price": self.get_total_price(),
            "total_discount": self.get_total_discount(),
            "coupon_discount": coupon_discount,
            "total_price_after_discount": final_total,
        }


