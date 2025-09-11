from django.urls import path, include
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
]


from django.urls import re_path

from dj_rest_auth.app_settings import api_settings
from rest_framework.routers import DefaultRouter

from dj_rest_auth.views import (
    LogoutView
)

router = DefaultRouter()

# Add JWT  URLs / OAuth2 URLs
from apps.accounts.views import RegisterView, LoginView, SendOTPView, VerifyOTPView, \
                                PasswordChangeView, PasswordResetConfirmView, PasswordResetView, \
                                AddressViewSet, CheckLoginView


    # Register the AddressViewSet with the router
router.register("addresses", AddressViewSet, basename="address")

urlpatterns += [
    path('check/', CheckLoginView.as_view(), name='check_login'),
    path('registration/', RegisterView.as_view(), name='registration'),

    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
     # URLs that do not require a session or valid token
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),

    path('password/reset/confirm/',PasswordResetConfirmView.as_view(),name='password_reset_confirm'),



    # URLs that require a user to be logged in with a valid session / token.
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'), #there is aproblem make it must authentication

    path("otp/request/", SendOTPView.as_view(), name="otp_request"),
    path("otp/verify/", VerifyOTPView.as_view(), name="otp_verify"),

    path("google/", include("allauth.socialaccount.urls")),
]



from apps.store.views import ProductListView, ProductDetailView, WishlistListView, WishlistAddView, WishlistRemoveView

urlpatterns += [

    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    path("wishlist/", WishlistListView.as_view(), name="wishlist-list"),
    path("wishlist/add/", WishlistAddView.as_view(), name="wishlist-add"),
    path("wishlist/remove/", WishlistRemoveView.as_view(), name="wishlist-remove"),

]

from apps.reviews.views import ReviewCreateView, ReviewDestroyView, ReviewUpdateView
urlpatterns += [
    path("<slug:slug>/reviews/add/", ReviewCreateView.as_view(), name="review-add"),
    path("<slug:slug>/reviews/remove/", ReviewDestroyView.as_view(), name="review-remove"),
    path("<slug:slug>/reviews/update/", ReviewUpdateView.as_view(), name="review-update"),

]


from apps.cart.views import CartListView, CartAddView, CartRemoveView, CartClearView, CartPromotionDeactivateView, CartPromotionReactivateView

urlpatterns += [
    path("cart/", CartListView.as_view(), name="cart-list"),
    path("cart/add/<slug:slug>/", CartAddView.as_view(), name="cart-add"),
    path("cart/remove/<slug:slug>/", CartRemoveView.as_view(), name="cart-remove"),
    path("cart/clear/", CartClearView.as_view(), name="cart-clear"),
    path("promotion/deactivate/<slug:slug>/", CartPromotionDeactivateView.as_view(), name="cart_promo_deactivate"),
    path("promotion/reactivate/<slug:slug>/", CartPromotionReactivateView.as_view(), name="cart_promo_reactivate"),
]
from apps.orders.views import OrderCancelView, OrderCreateView, OrderDetailView, OrderListView
urlpatterns += [
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<uuid:id>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<uuid:id>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
]
from rest_framework.routers import DefaultRouter
from apps.sellers.views import (
    SellerViewSet,
    BankAccountViewSet,
    TaxInfoViewSet,
    ProductViewSet,
    OrderViewSet,
    PayoutViewSet,
)



router.register('sellers', SellerViewSet, basename='seller')
router.register('sellers-bank-accounts', BankAccountViewSet, basename='bankaccount')
router.register('sellers-tax-info', TaxInfoViewSet, basename='taxinfo')
router.register('seller-products', ProductViewSet, basename='seller_products')
router.register('seller-orders', OrderViewSet, basename='seller_orders')
router.register('seller-payouts', PayoutViewSet, basename='seller_payout')

urlpatterns += [
    path("", include(router.urls)),
]
# make shipping system
# add payments system
# make seller system
# Make Advertisement system
# link order system with payments and address system
# make Notification system
# add loyalty program

# make Home page
# make contact us page
# make newsletter system
# make about us page
# make terms and conditions page
# make privacy policy page


# enhance system overall
# improve performance and scalability
# ensure security best practices
# make tests in system overall