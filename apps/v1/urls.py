from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
]


from django.urls import re_path

from dj_rest_auth.app_settings import api_settings

from dj_rest_auth.views import (
    LogoutView
)




# Add JWT  URLs / OAuth2 URLs
from apps.accounts.views import RegisterView, LoginView, SendOTPView, VerifyOTPView, \
                                PasswordChangeView, PasswordResetConfirmView, PasswordResetView
urlpatterns += [
    path('registration/', RegisterView.as_view(), name='registration'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
     # URLs that do not require a session or valid token
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),

    path('password/reset/confirm/',PasswordResetConfirmView.as_view(),name='password_reset_confirm'),

    path('login/', LoginView.as_view(), name='login'),
    
    # URLs that require a user to be logged in with a valid session / token.
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),

    path("otp/request/", SendOTPView.as_view(), name="otp_request"),
    path("otp/verify/", VerifyOTPView.as_view(), name="otp_verify"),

    path("google/", include("allauth.socialaccount.urls")),
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
    path("cart/<slug:slug>/add/", cart_add, name="cart-add"),
    path("cart/<slug:slug>/update/", cart_update, name="cart-update"),
    path("cart/<slug:slug>/remove/", cart_remove, name="cart-remove"),
    path("cart/<slug:slug>/clear/", cart_clear, name="cart-clear"),
]

from apps.coupons.views import apply_coupon
urlpatterns += [
    path("coupons/apply/", apply_coupon, name="apply-coupon"),
]
#  Cart Price -->  coupon applyied
#  checkout  / total price --> Cart Price -order promotion + shipping cost
# apply promotions and coupon in cart and checkout and order as [Guest , User]
# create order , order now , order lists , order details and order cancel as [Guest , User]
# make address create/destroy/edit 
# make full scenario for guest and user and check flow bugs
# review accounts system
# add payments system
# add loyalty program

# make Home page
# make Notification system
# make Payment system
# make contact us page
# make newsletter system
# make about us page
# make terms and conditions page
# make privacy policy page


# enhance system overall
# improve performance and scalability
# ensure security best practices