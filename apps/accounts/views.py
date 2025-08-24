from django.forms import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login as django_login, get_user_model, logout
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.mail import send_mail

from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, AddressSerializer
from .models import Address

from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.models import TokenModel
from django.utils import timezone
from dj_rest_auth.jwt_auth import set_jwt_cookies
from dj_rest_auth.utils import jwt_encode
from core.utils import get_client_ip
import random



sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password1', 'password2'),)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = api_settings.REGISTER_PERMISSION_CLASSES
    token_model = TokenModel
    throttle_scope = 'dj_rest_auth'

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        user.verified = False
        user.save()

        # توليد كود OTP
        otp = random.randint(100000, 999999)
        cache.set(f"otp_{user.email}", otp, timeout=300)

        # send_mail(
        #     subject="Your OTP Code",
        #     message=f"Your OTP code is {otp}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        #     fail_silently=False,
        # )
        print(f"OTP sent to {user.email}: {otp}")

        return Response(
            {"message": "Account created. OTP sent to your email. Please verify.", "OTP": otp},
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        return user

class SendOTPView(APIView):
    """
    إرسال OTP إلى إيميل المستخدم
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # توليد كود OTP
        otp = random.randint(100000, 999999)

        # نخزنه مؤقتًا في cache (مدته 5 دقائق)
        cache.set(f"otp_{email}", otp, timeout=300)

        # إرسال OTP على الإيميل
        # send_mail(
        #     subject="Your OTP Code",
        #     message=f"Your OTP code is {otp}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[email],
        #     fail_silently=False,
        # )
        print(f"OTP sent to {email}: {otp}")
        return Response({"message": "OTP sent to email", "OTP": otp}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    """
    التحقق من الـ OTP
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)


        cached_otp = cache.get(f"otp_{email}")
        if cached_otp and str(cached_otp) == str(otp):
            cache.delete(f"otp_{email}")
            user = get_user_model().objects.filter(email=email).first()
            if user:
                user.verified = True
                user.save()
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_scope = 'dj_rest_auth'

    user = None
    access_token = None
    token = None

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        if api_settings.JWT_AUTH_RETURN_EXPIRATION:
            response_serializer = api_settings.JWT_SERIALIZER_WITH_EXPIRATION
        else:
            response_serializer = api_settings.JWT_SERIALIZER

        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        self.access_token, self.refresh_token = jwt_encode(self.user)

        if api_settings.SESSION_LOGIN:
            self.process_login()
 
    def get_response(self):
        serializer_class = self.get_response_serializer()

        from rest_framework_simplejwt.settings import (
            api_settings as jwt_settings,
        )
        access_token_expiration = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
        refresh_token_expiration = (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
        return_expiration_times = api_settings.JWT_AUTH_RETURN_EXPIRATION
        auth_httponly = api_settings.JWT_AUTH_HTTPONLY
        data = {
            'user': self.user.email,
            'access': self.access_token,
        }
        if not auth_httponly:
            data['refresh'] = self.refresh_token
        else:
            # Wasnt sure if the serializer needed this
            data['refresh'] = ""
        if return_expiration_times:
            data['access_expiration'] = access_token_expiration
            data['refresh_expiration'] = refresh_token_expiration
        serializer = serializer_class(
            instance=data,
            context=self.get_serializer_context(),
        )
            
        response = Response(serializer.data, status=status.HTTP_200_OK)
        set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


User = get_user_model()


class PasswordResetView(GenericAPIView):
    """
    Step 1: Request OTP for password reset.
    Accepts: email
    Sends OTP to user's email.
    """
    permission_classes = (AllowAny,)
    throttle_scope = 'dj_rest_auth'

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # توليد OTP
        otp = random.randint(100000, 999999)
        cache.set(f"reset_otp_{email}", otp, timeout=300)  # 5 دقايق صلاحية

        # send_mail(
        #     subject="Password Reset OTP",
        #     message=f"Your OTP for password reset is {otp}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[email],
        # )
        print(f"Password Reset OTP for {email}: {otp}")

        return Response(
            {'detail': _('OTP has been sent to your email.'), 'OTP': otp},  # فقط للاختبار، احذفها في الإنتاج
            status=status.HTTP_200_OK,
        )

@method_decorator(sensitive_post_parameters('password1', 'password2', 'new_password1', 'new_password2'), name='dispatch')
class PasswordResetConfirmView(GenericAPIView):
    """
    Step 2: Confirm OTP and reset password.
    Accepts: email, otp, new_password1, new_password2
    """
    permission_classes = (AllowAny,)
    throttle_scope = 'dj_rest_auth'


    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp = request.data.get("otp")
        password1 = request.data.get("new_password1")
        password2 = request.data.get("new_password2")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            return Response({"error": "OTP is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password1:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password2:
            return Response({"error": "Confirm new password is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password1)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if password1 != password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(f"reset_otp_{email}")
        if not cached_otp or str(cached_otp) != str(otp):
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # تغيير الباسورد
        user.set_password(password1)
        user.save()

        # مسح الـ OTP
        cache.delete(f"reset_otp_{email}")

        # حذف التوكن القديم (logout)
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        # حذف كل التوكنات القديمة (JWT)
        try:
            RefreshToken.for_user(user)
        except Exception:
            pass

        return Response(
            {'detail': _('Password has been reset successfully.')},
            status=status.HTTP_200_OK,
        )


@method_decorator(sensitive_post_parameters('old_password', 'new_password1', 'new_password2'), name='dispatch')
class PasswordChangeView(GenericAPIView):
    """
    Change password (for logged in users).
    Accepts: new_password1, new_password2
    """
    permission_classes = (IsAuthenticated,)
    throttle_scope = 'dj_rest_auth'
    def post(self, request, *args, **kwargs):
        old_password = request.data.get("old_password")
        password1 = request.data.get("new_password1")
        password2 = request.data.get("new_password2")

        if not old_password:
            return Response({"error": "Old password is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not password1 or not password2:
            return Response({"error": "Both new password fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if password1 != password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password1, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password1)
        user.save()

        # حذف التوكن القديم (logout)
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        # حذف كل التوكنات القديمة (JWT)
        try:
            RefreshToken.for_user(user)
        except Exception:
            pass

        logout(request)

        return Response({'detail': _('New password has been saved. Please login again.')}, status=status.HTTP_200_OK)



class AddressViewSet(viewsets.ModelViewSet):

    serializer_class = AddressSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Address.objects.filter(user=self.request.user)
        else:
            return Address.objects.filter(ip_address=get_client_ip(self.request))

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(ip_address=get_client_ip(self.request))

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """
        تعيين عنوان كافتراضي
        """
        address = self.get_object()
        if self.request.user.is_authenticated:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        else:
            Address.objects.filter(ip_address=get_client_ip(self.request), is_default=True).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({"status": "تم تعيين العنوان كافتراضي"}, status=status.HTTP_200_OK)
