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

from apps.reviews.views import ReviewCreateView, ReviewDestroyView
urlpatterns += [
    path("<slug:slug>/reviews/add/", ReviewCreateView.as_view(), name="review-add"),
    path("<slug:slug>/reviews/remove/", ReviewDestroyView.as_view(), name="review-remove"),

]
from apps.cart.views import CartListView, cart_add, cart_update, cart_remove, cart_clear
urlpatterns += [

    path("cart/", CartListView.as_view(), name="cart-list"),
    path("cart/<slug:slug>/add/", cart_add.as_view(), name="cart-add"),
    path("cart/<slug:slug>/update/", cart_update.as_view(), name="cart-update"),
    path("cart/<slug:slug>/remove/", cart_remove.as_view(), name="cart-remove"),
    path("cart/<slug:slug>/clear/", cart_clear.as_view(), name="cart-clear"),
]

#  Cart Price -->  coupon applyied
#  checkout  / total price --> Cart Price -order promotion + shipping cost

# apply promotions and coupon in cart and checkout and order as [Guest , User]

# create order , order now , order lists , order details and order cancel as [Guest , User]

# make Home page
# make Notification system
# make Payment system
# make contact us page
# make newsletter system
# make about us page
# make terms and conditions page
# make privacy policy page