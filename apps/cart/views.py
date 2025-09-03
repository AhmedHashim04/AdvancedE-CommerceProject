from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from rest_framework import generics
from rest_framework import permissions
from apps.store.models import Product
from apps.cart.cart import Cart 
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
    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:
        return JsonResponse({"error": "Quantity must be greater than 0"}, status=400)
    cart.add(product=product, quantity=quantity)
    return JsonResponse({
        "message": "Product added to cart",
        "product": slug,
        "quantity": quantity,
    }, status=200)

@require_POST
@csrf_exempt
def cart_update(request, slug):
    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:
        cart.remove(product)
    else:
        cart.add(product=product, quantity=quantity)
    return JsonResponse({
        "message": "Product updated in cart",
        "product": slug,
        "quantity": cart.cart.get(str(product.slug), {}).get("quantity", 0),
    }, status=200)

@csrf_exempt
@require_POST
def cart_remove(request, slug):
    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug)
    cart.remove(product)
    return JsonResponse({
        "message": "Product removed from cart",
        "product": slug,
    }, status=200)

@csrf_exempt
@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return JsonResponse({"message": "Cart cleared"}, status=200)

class CartListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        return Response({
            "items": list(cart),
            "total_items": cart.get_total_items(),
            "distinct_items": cart.get_distinct_items(),
            "total": cart.get_total(),
            "total_tax": cart.get_total_tax(),
        })
