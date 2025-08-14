from rest_framework import serializers
from .models import Product, ShippingClass, ProductColor
from django.core.cache import cache
import hashlib


class ShippingClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingClass
        fields = ('name', 'description', 'price')

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ('name', 'hex_code')

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    brand_name = serializers.ReadOnlyField(source='brand.name')
    shipping_class = ShippingClassSerializer()
    tags = serializers.SerializerMethodField()
    color_options = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'slug', 'description', 'short_description', 'sku',
                'barcode', 'brand_name', 'category_name', 'tags', 'price', 'compare_at_price',
                'discount_percentage', 'cost_price', 'currency', 'tax_rate',
                'stock_quantity', 'low_stock_threshold', 'is_in_stock',
                'allow_backorder', 'main_image', 'gallery', 'video_url',
                'view_360_url', 'weight', 'width', 'height', 'depth',
                'shipping_class', 'meta_title', 'meta_description', 'meta_keywords',
                'has_variants', 'attributes', 'color_options', 'is_active', 'is_featured',
                'created_at', 'updated_at', 'views_count', 'sales_count')
        # depth = 1



    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_color_options(self, obj):
        return [color.name for color in obj.color_options.all()]

    def get_gallery(self, obj):
        return [photo.image.url for photo in obj.gallery.all()]

    # # Slow
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['tags'] = [tag.name for tag in instance.tags.all()]
    #     data['color_options'] = [color.name for color in instance.color_options.all()]
    #     data['gallery'] = [photo.image.url for photo in instance.gallery.all()]
    #     return data

    # # little Slow
    # def to_representation(self, instance):
    #     # 1) بناء Key للكاش
    #     cache_key = f"product_serializer:{instance.pk}:{instance.updated_at.timestamp()}"
    #     data = cache.get(cache_key)

    #     if data is not None:
    #         return data  # 2) لو موجود في الكاش يرجع على طول

    #     # 3) اعمل serialization عادي
    #     data = super().to_representation(instance)

    #     # علاقات إضافية
    #     data['tags'] = [tag.name for tag in instance.tags.all()]
    #     data['color_options'] = [color.name for color in instance.color_options.all()]
    #     data['gallery'] = [photo.image.url for photo in instance.gallery.all()]

    #     # 4) احفظ في الكاش (مثلاً لمدة 10 دقايق)
    #     cache.set(cache_key, data, timeout=600)

    #     return data
