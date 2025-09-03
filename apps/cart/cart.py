from django.conf import settings
from django.core.cache import cache
from decimal import Decimal


class ShoppingCart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.cart = self._get_cart_items
    
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

        
    def add(self, product, quantity):
        if not product.pk:
            return
        if quantity <= 0:
            self.remove(product)
            return
        slug = str(product.slug)
        item =self.cart.get(slug)
        if item:
            item.get("quantity") += quantity
            # TODO : handle promotion
            return
        price = Decimal(product.final_price)

        self.cart.update({slug:{"quantity":quantity,"price":price
                               ,"promotion":product.getPromotion.handle_bqg(product,self.cart) if product.getPromotion else None}})

    def remove(self, product):
        pass
    def update_quantity(self, product, quantity):
        pass
    def clear(self):
        pass
    def get_total_price(self):
        pass
    def __len__(self):
        pass




    @staticmethod
    def merge_on_login(user, old_session_key) -> int:
        session_cart_key = f"cart_session_{old_session_key}"
        user_cart_key = f"cart_user_{user.id}"

        session_cart = cache.get(session_cart_key, {})
user_cart = cache.get(user_cart_key, {})

        merged_cart user_cart.copy()
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
