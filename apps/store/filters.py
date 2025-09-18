import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    template = None  # يمنع محاولة تحميل أي template
    ordering = django_filters.OrderingFilter(
        fields=(
            ('base_price', 'base_price'),
            ('created_at', 'created_at'),
            ('name', 'name'),
        ),

        field_labels={
            'base_price': 'base_price',
            'created_at': 'Created Date',
            'name': 'Product Name',
        }
    )

    class Meta:
        model = Product
        fields = {
            'base_price': ['exact', 'gte', 'lte'],
            'is_active': ['exact'],
            'created_at': ['gte', 'lte'],
            'name': ['icontains'],
            'description': ['icontains'],
            'short_description': ['icontains'],
        }
