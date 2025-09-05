from rest_framework import serializers
from .models import Product, ProductColor
from django.core.cache import cache
import hashlib

class DynamicFieldsProductSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields = None
        if "request" in self.context and "fields" in self.context:
            fields = self.context["fields"]
            fields.remove("brand")
            fields.append("brand_name")
            fields.remove("category")
            fields.append("category_name")

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# class ShippingClassSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShippingClass
#         fields = ('name', 'description', 'price')


class ProductSerializer(DynamicFieldsProductSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    brand_name = serializers.ReadOnlyField(source='brand.name')
    # shipping_class = ShippingClassSerializer()
    tags = serializers.SerializerMethodField()
    color_options = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    promotion = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"
    
    def get_final_price(self, obj):
        return str(obj.final_price) if obj.final_price else None

    def get_promotion(self, obj):
        return str(obj.promotion) if obj.promotion else None

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_color_options(self, obj):
        return [color.name for color in obj.color_options.all()]

    def get_gallery(self, obj):
        return None#[photo.image.url for photo in obj.gallery.all()]

    def get_reviews(self, obj):
        return [(review.user.email if review.user else review.ip_address, review.rating, review.feedback) for review in obj.reviews.all()]


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
