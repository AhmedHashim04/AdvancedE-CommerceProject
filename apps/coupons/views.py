from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.cart.cart import Cart as ShoppingCart
from .models import Coupon, CouponRedemption

from django.db import transaction

@api_view(['POST'])
def apply_coupon(request):
    code = request.data.get("code")
    user = request.user if request.user.is_authenticated else None

    if not code:
        return Response({"error": "Coupon code is required."}, status=400)

    cart = ShoppingCart(request)

    with transaction.atomic():
        # Lock row to prevent race conditions
        coupon = Coupon.objects.select_for_update().get(code=code) # Lock على صف الكوبون أثناء التحقق والتعديل.

        # validate
        is_valid, error_message = coupon.is_valid(cart_total=cart.get_total_price(), user=user)
        if not is_valid:
            return Response({"error": error_message}, status=400)

        # apply discount
        discount, message = coupon.apply_discount(cart=cart)

        # save coupon usage
        if user:
            CouponRedemption.objects.create(coupon=coupon, user=user)

        # save coupon in session
        request.session['applied_coupon_id'] = coupon.id

    return Response({
        "success": True,
        "discount": str(discount),
        "message": message
    }, status=200)

@api_view(['POST'])
def remove_coupon(request):
    if 'applied_coupon_id' in request.session:
        del request.session['applied_coupon_id']
        return Response({"success": True, "message": "Coupon removed."})
    return Response({"success": False, "message": "No coupon to remove."}, status=status.HTTP_400_BAD_REQUEST)

