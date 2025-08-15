from .models import Product
from rest_framework import generics
from rest_framework.response import Response
from .serializers import ProductSerializer
import hashlib
import json
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.pagination import CursorPagination

class CursorPagination(CursorPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'page_size' 
    ordering = '-created_at'

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.select_related(
            'category', 'brand', 'shipping_class'
        ).prefetch_related(
            'tags', 'color_options', 'gallery'
        ).filter(is_active=True,is_in_stock=True
        ).only(
            'name', 'slug',  'short_description',
            'brand', 'category', 'tags',
            'price', 'compare_at_price', 'discount_percentage', 'currency', 'tax_rate',
            'stock_quantity',
            'allow_backorder', 
            'main_image', 'gallery',
            'shipping_class', 'attributes', 'is_featured',

        )


    def list(self, request, *args, **kwargs):
        # نحدد مفتاح الكاش بناءً على الفلاتر + الباجينيشن
        params_string = json.dumps(request.query_params, sort_keys=True)
        key_hash = hashlib.md5(params_string.encode()).hexdigest()
        cache_key = f"products:{key_hash}"

        # نحاول نجيب النتيجة من الكاش
        cached_response = cache.get(cache_key)
        if cached_response:
            print(cached_response)
            return Response(cached_response)

        # لو مفيش كاش، ننفذ الطريقة العادية
        response = super().list(request, *args, **kwargs)

        cache.set(cache_key, response.data, timeout=60 * 60 * 12)

        return response

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    max_related_products = 4
    max_recently_viewed = 5

    def get_queryset(self):
        return (
            Product.objects.select_related(
                'category', 'brand', 'shipping_class'
            )
            .prefetch_related(
                'tags', 'color_options', 'gallery'
            )
            .filter(is_active=True,is_in_stock=True)
            .only(
                'id', 'name', 'slug', 'description', 'sku','barcode', 
                'price', 'compare_at_price','discount_percentage', 'cost_price', 'currency', 'tax_rate',
                'category', 'brand',
                'stock_quantity', 'is_in_stock',
                'allow_backorder', 'main_image', 'video_url', 'view_360_url',
                'weight', 'width', 'height', 'depth',
                'shipping_class_id',
                'meta_title', 'meta_description', 'meta_keywords',
                'has_variants', 'attributes', 'is_featured',
                'views_count', 'sales_count'
            )
        )

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()

        self.update_recently_viewed(product)

        data = ProductSerializer(product).data
        # المنتجات المرتبطة
        related = self.get_related_products_context(product)["related_products"]
        data["related_products"] = related

        # المنتجات المشاهدة مؤخرًا
        recently = self.get_recently_viewed_products(product)
        data["recently_viewed"] = recently


        return Response(data)

    def get_related_products_context(self, product):
        max_related = self.max_related_products
        excluded_ids = {product.id}

        related_products = list(
            Product.objects.filter(category=product.category,is_active=True,is_in_stock=True)
            .exclude(id=product.id)
            .select_related('category'
            ).values('id','category__name', 'name', 'slug', 'main_image')
            [:max_related]
        )

        excluded_ids.update(p.get('id') for p in related_products)

        if product.category and len(related_products) < max_related:
            parent_category = product.category.parent
            if parent_category:
                additional_products =Product.objects.filter(
                category=product.category,is_active=True,is_in_stock=True
                ).exclude(id__in=excluded_ids
                ).values('id','category__name', 'name', 'slug', 'main_image')[
                    :max_related - len(related_products)
                ]
                related_products += list(additional_products)

        related_products = related_products[:max_related]

        return {'related_products': related_products}

    def get_recently_viewed_products(self, product):
        session_key = 'recently_viewed'
        viewed_slugs = self.request.session.get(session_key, [])

        if product.slug in viewed_slugs:
            viewed_slugs.remove(product.slug)
        viewed_slugs = viewed_slugs[:self.max_recently_viewed]

        return Product.objects.filter(
            category=product.category,is_active=True,is_in_stock=True,
            slug__in=viewed_slugs
        ).values('id','category__name', 'name', 'slug', 'main_image',
        "price","discount_percentage","currency","tax_rate","compare_at_price"
        ).exclude(slug=product.slug)

    def update_recently_viewed(self, product):
        session_key = 'recently_viewed'
        viewed_slugs = self.request.session.get(session_key, [])

        if product.slug in viewed_slugs:
            viewed_slugs.remove(product.slug)
        viewed_slugs.insert(0, product.slug)

        viewed_slugs = viewed_slugs[:self.max_recently_viewed]
        self.request.session[session_key] = viewed_slugs
        self.request.session.modified = True



