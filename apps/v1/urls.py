from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
]

# Add JWT  URLs / OAuth2 URLs

from apps.accounts.views import RegisterView, ChangePasswordView, ForgetPasswordView, ResetPasswordConfirmView, ResetPasswordOTPConfirmView
urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("dj-rest-auth/google/", include("allauth.socialaccount.urls")),

    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    path("forget-password/", ForgetPasswordView.as_view(), name="forget-password"),

    # لو المستخدم فتح اللينك اللي فيه JWT
    path("reset-password/", ResetPasswordConfirmView.as_view(), name="reset-password"),

    # لو المستخدم عايز يستخدم OTP بدل اللينك
    path("reset-password-otp/", ResetPasswordOTPConfirmView.as_view(), name="reset-password-otp"),
]

from apps.store.views import ProductListView, ProductDetailView, WishlistListView, WishlistAddView, WishlistRemoveView

urlpatterns += [

    path("products/", ProductListView.as_view(), name="product-list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    path("wishlist/", WishlistListView.as_view(), name="wishlist-list"),
    path("wishlist/add/", WishlistAddView.as_view(), name="wishlist-add"),
    path("wishlist/remove/", WishlistRemoveView.as_view(), name="wishlist-remove"),
    
]
# Review add / remove as [user / guest ]

urlpatterns += [
    path("<slug:slug>/reviews/", ReviewListView.as_view(), name="product-list"),
    path("<slug:slug>/add/", ReviewCreateView.as_view(), name="wishlist-add"),
    path("<slug:slug>/remove/", ReviewDeleteView.as_view(), name="wishlist-remove"),

]

# aplly coupon / discounts and promotions in discount cart and checkout and order as [user / guest ]
# create order , order now , order lists , order details and order cancel as [user / guest ]
# make Home page
# make Notification system
# make Payment system
# make contact us page
# make newsletter system
# make about us page
# make terms and conditions page
# make privacy policy page