from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Coupon, CouponRedemption

@api_view(['POST'])
def apply_coupon(request):
    coupon_code = request.data.get("coupon_code")
    user = request.user if request.user.is_authenticated else None

    if not coupon_code:
        return Response({"error": "Coupon code is required."}, status=status.HTTP_400_BAD_REQUEST)

    coupon = get_object_or_404(Coupon, code=coupon_code)    

    # validate
    is_valid, error_message = coupon.is_valid(user=user)
    if not is_valid:
        return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    # apply discount
    discount, message = coupon.apply_discount()

    # save coupon usage
    if user:
        CouponRedemption.objects.create(coupon=coupon, user=user)

    # save coupon in session
    request.session['applied_coupon_id'] = coupon.id

    return Response({
        "success": True,
        "discount": str(discount),
        "message": message
    }, status=status.HTTP_200_OK)
