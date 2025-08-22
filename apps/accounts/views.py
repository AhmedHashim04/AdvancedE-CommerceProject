from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer
from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.models import TokenModel
from django.contrib.auth import login as django_login, get_user_model
from django.utils import timezone
from dj_rest_auth.jwt_auth import set_jwt_cookies
from rest_framework.permissions import AllowAny
from dj_rest_auth.utils import jwt_encode
from rest_framework.views import APIView
import random
from django.core.cache import cache
from django.core.mail import send_mail


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
            {"message": "Account created. OTP sent to your email. Please verify."},
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
        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)

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

