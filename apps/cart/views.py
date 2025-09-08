
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import permissions
from apps.promotions.models import Promotion
from apps.store.models import Product
from apps.cart.cart import ShoppingCart
from django.utils.translation import gettext as _
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# from django_ratelimit.decorators import ratelimit


# @ratelimit(key='ip', rate='100/m', method='POST', block=True)

@require_POST
@csrf_exempt
def cart_add(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        return JsonResponse({"error": "Quantity must be greater than 0"}, status=400)

    cart.add(product=product, quantity=quantity)

    return JsonResponse({
        "message": "Product added to cart",
        "product": slug,
        "promotion": cart.cart[slug].get("promotion"),
        "quantity": quantity,
        "cart": cart.cart,
    }, status=200)

# @ratelimit(key='ip', rate='10/m', method='POST', block=True)
@csrf_exempt
@require_POST
def cart_remove(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    if product.slug not in cart.cart:
        return JsonResponse({"error": "Product not in cart"}, status=400)
    cart.remove(product)

    return JsonResponse({
        "message": "Product removed from cart",
        "product": slug,
    }, status=200)

@csrf_exempt
@require_POST
def cart_clear(request):
    cart = ShoppingCart(request)
    cart.clear()

    return JsonResponse({"message": "Cart cleared"}, status=200)

class CartListView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        cart = ShoppingCart(request)
        cart_summary = cart.get_cart_summary()
        return Response({
            "cart": cart.cart,  # or serialize as needed
            "cart_summary": cart_summary
        })
    

from apps.cart.cart import ShoppingCart
# active / disactive promotion
@csrf_exempt
@require_POST
def cart_active_promotion(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    cart.active_promotion(product)
    return JsonResponse({"message": "Promotion activated"}, status=200)

@csrf_exempt
@require_POST
def cart_disactive_promotion(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    cart.disactive_promotion(product)
    return JsonResponse({"message": "Promotion deactivated"}, status=200)
