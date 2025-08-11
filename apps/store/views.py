from rest_framework import generics
from .serializers import ProductSerializer
from .models import Product
from django_filters.rest_framework import DjangoFilterBackend

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'price': ['exact', 'gte', 'lte'],
        'discount_percentage': ['gte', 'lte'],
        'is_active': ['exact'],
        'created_at': ['gte', 'lte'],
        'name': ['icontains'],
    }