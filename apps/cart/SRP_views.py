from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from apps.store.models import Product  
from .utils import get_cart

class CartListView(APIView):
    """
    View the contents of the cart + summary
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        cart = get_cart(request)
        cart_summary = cart.summary()

        return Response({
            "auth": request.user.is_authenticated,
            "cart": cart,
            "cart_summary": cart_summary
        }, status=status.HTTP_200_OK)


class CartAddView(APIView):
    """
    Add a product to the cart
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)

        quantity = int(request.data.get("quantity", 1))

        cart = get_cart(request)
        cart = cart.add_product(product, quantity)


        return Response({
            "message": "Product added to cart",
            "cart": cart,
            "summary": cart.summary()
        }, status=status.HTTP_200_OK)


class CartRemoveView(APIView):
    """
    Remove a product from the cart
    """
    permission_classes = [permissions.AllowAny]

    def delete(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)

        cart = get_cart(request)
        cart = cart.remove_product(product)

        return Response({
            "message": "Product removed from cart",
            "cart": cart,
            "summary": cart.summary()
        }, status=status.HTTP_200_OK)


class CartClearView(APIView):
    """
    Clear the cart completely
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        cart = cart.clear()

        return Response({
            "message": "Cart cleared",
            "cart": cart,
            "summary": cart.summary()
        }, status=status.HTTP_200_OK)



class CartPromotionDeactivateView(APIView):
    """
    Deactivate a promotion for a specific product in the cart
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)

        cart = get_cart(request)
        cart = cart.deactive_promotion(product)

        return Response({
            "message": "deactivated promotion for this product",
            "cart": cart,
            "summary": cart.summary()
        }, status=status.HTTP_200_OK)


class CartPromotionReactivateView(APIView):
    """
    Reactivate a promotion for a specific product in the cart
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)

        cart = get_cart(request)
        cart.reactive_promotion(product)

        return Response({
            "message": "Reactivate promotion for this product",
            "cart": cart,
            "summary": cart.summary()
        }, status=status.HTTP_200_OK)
