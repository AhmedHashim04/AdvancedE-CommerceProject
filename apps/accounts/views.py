from rest_framework import generics
from .serializers import RegisterSerializer, ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser as User

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


class WhishListView(generics.ListCreateAPIView):
    pass

class AdressListView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    pass