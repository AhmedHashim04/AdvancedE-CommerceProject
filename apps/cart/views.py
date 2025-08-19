from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import generics
from rest_framework import permissions
from apps.store.models import Product
from .cart import Cart as ShoppingCart
from django.utils.translation import gettext as _
# from django_ratelimit.decorators import ratelimit


# @ratelimit(key='ip', rate='100/m', method='POST', block=True)
@require_POST
def cart_add(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:raise ValueError
    cart.add(product=product, quantity=quantity)

# @ratelimit(key='ip', rate='20/m', method='POST', block=True)
@require_POST
def cart_update(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:raise ValueError
    cart.add(product=product, quantity=quantity)

# @ratelimit(key='ip', rate='10/m', method='POST', block=True)
@require_POST
def cart_remove(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    cart.remove(product)

@require_POST
def cart_clear(request):
    cart = ShoppingCart(request)
    cart.clear()

class CartListView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get_cart(self):
        return ShoppingCart(self.request)

    def get_cart_summary(self):
        return self.get_cart().get_cart_summary()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = self.get_cart()
        context["cart_summary"] = self.get_cart_summary()
        return context


