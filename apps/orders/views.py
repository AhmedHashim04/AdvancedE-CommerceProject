from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView
from core.utils import get_client_ip


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.filter(ip_address=get_client_ip(self.request))
    
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.filter(ip_address=get_client_ip(self.request))

class OrderCreateView(CreateAPIView):
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(ip_address=get_client_ip(self.request))

class OrderCancelView(DestroyAPIView):
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.filter(ip_address=get_client_ip(self.request))
