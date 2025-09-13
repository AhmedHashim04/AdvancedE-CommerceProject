from .serializers import AddressSerializer
from .models import Address
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.utils import get_client_ip

# Create your views here.


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
