from django.contrib import admin
from .models import Coupon, CouponRedemption

admin.site.register(Coupon)
admin.site.register(CouponRedemption)
