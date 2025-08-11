from rest_framework import serializers
from .models import Product, ShippingClass, ProductColor

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


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = [tag.name for tag in instance.tags.all()]
        data['color_options'] = [color.name for color in instance.color_options.all()]
        data['gallery'] = [photo.image.url for photo in instance.gallery.all()]
        return data