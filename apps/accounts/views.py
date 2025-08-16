from rest_framework import generics
from .serializers import RegisterSerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from decouple import config  
from rest_framework import status
from rest_framework.response import Response
from .serializers import ForgetPasswordSerializer
from .models import CustomUser as User, PasswordResetOTP
from .utils import generate_reset_jwt, generate_otp, decode_reset_jwt
from django.contrib.auth.hashers import make_password

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)


        user = self.get_object()
        refresh = RefreshToken.for_user(user)

        response.data = {
            'user': RegisterSerializer(instance=user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return response

class ForgetPasswordView(generics.CreateAPIView):
    serializer_class = ForgetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # 1️⃣ توليد JWT link
        token = generate_reset_jwt(user.id)
        reset_link = f"{config('HOST')}/reset-password/?token={token}"

        # 2️⃣ توليد OTP
        otp = generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)

        # 3️⃣ إرسال الإيميل (HTML)
        subject = "Password Reset"
        message = f"Click the link: {reset_link}\nOr use the code: {otp}"
        html_message = f"""
        <html>
          <body style="font-family:Arial;">
            <h2 style="color:#007bff;">🔑 Password Reset</h2>
            <p>Click the button to change your password:</p>
            <a href="{reset_link}" style="background:#007bff;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">Reset Password Now</a>
            <p>Or enter the following code:</p>
            <h3 style="color:#333;">{otp}</h3>
            <p>The code is valid for 10 minutes only.</p>
          </body>
        </html>
        """

        send_mail(
            subject,
            message,
            config('EMAIL_HOST_USER'),
            [email],
            html_message=html_message,
        )

        return Response(
            {"detail": "We have sent a password reset link and OTP code to your email."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirmView(generics.CreateAPIView):
    """
    The user opens the link in the JWT and enters a new password
    """
    def create(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            return Response({"error": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_reset_jwt(token)
        if not payload:
            return Response({"error": "Invalid or expired link"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=payload["user_id"])
            user.password = make_password(new_password)
            user.save()
            return Response({"detail": "Password has been changed successfully ✅"})
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordOTPConfirmView(generics.CreateAPIView):
    """
    The user enters the OTP code and a new password
    """
    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("password")

        if not email or not otp or not new_password:
            return Response({"error": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).last()

            if not otp_obj or not otp_obj.is_valid():
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

            user.password = make_password(new_password)
            user.save()
            return Response({"detail": "Password has been changed using OTP ✅"})
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

class WhishListView(generics.ListCreateAPIView):
    pass

class AdressListView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    pass