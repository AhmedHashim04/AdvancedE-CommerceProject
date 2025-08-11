from .models import Product
from rest_framework import generics
from .serializers import ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.pagination import CursorPagination

class CursorPagination(CursorPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'page_size' 

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    
