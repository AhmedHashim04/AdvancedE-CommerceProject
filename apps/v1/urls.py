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

from apps.store.views import ProductListView, ProductDetailView
urlpatterns += [

    path("products/", ProductListView.as_view(), name="product-list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    
]

urlpatterns += [

]