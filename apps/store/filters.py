import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    template = None  # يمنع محاولة تحميل أي template
    ordering = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('created_at', 'created_at'),
            ('name', 'name'),
        ),

        field_labels={
            'price': 'Price',
            'created_at': 'Created Date',
            'name': 'Product Name',
        }
    )

    class Meta:
        model = Product
        fields = {
            'price': ['exact', 'gte', 'lte'],
            'is_active': ['exact'],
            'created_at': ['gte', 'lte'],
            'name': ['icontains'],
            'description': ['icontains'],
            'short_description': ['icontains'],
            'currency': ['exact'],
        }
