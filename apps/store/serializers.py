from rest_framework import serializers
from .models import Product, ProductColor
from django.core.cache import cache
import hashlib
from rest_framework import serializers
from .models import Product, Brand, Category, Tag, ProductColor, ProductImage
from apps.promotions.models import Promotion

class PromotionSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = ["id", "type", "summary"]

    def get_summary(self, obj):
        # لو عايز تباصي كمية الشراء لحساب BQG
        bought_qty = self.context.get("bought_qty", 1)
        return obj.summary(bought_qty)


class BrandMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]

class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ["id", "name", "hex_code"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text"]

class DynamicFieldsProductSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields = None
        if "fields" in self.context:
            fields = self.context["fields"]

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProductSerializer(DynamicFieldsProductSerializer):
    brand = BrandMiniSerializer(read_only=True)
    category = CategoryMiniSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    color_options = ProductColorSerializer(many=True, read_only=True)
    gallery = ProductImageSerializer(many=True, read_only=True)
    pricing = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    # reviews = serializers.SerializerMethodField()

    seo = serializers.SerializerMethodField()
    promotion = PromotionSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "short_description", "description",
            "brand", "category", "tags", "color_options",
            "main_image", "gallery", "stock",
            "pricing", "promotion",
            "attributes", "is_featured", "seo",
            "created_at", "updated_at"
        ]

    # ---------- Nested & Custom Fields ----------

    def get_color_options(self, obj):
        return [
            {"id": color.id, "name": color.name, "hex": color.hex_code}
            for color in obj.color_options.all()
        ]

    def get_pricing(self, obj):
        return {
            "base_price": str(obj.base_price),
            "final_price": str(obj.final_price) if obj.final_price else None,
            "currency": obj.currency,
        }

    def get_stock(self, obj):
        return {
            "quantity": obj.stock_quantity,
            "allow_backorder": obj.allow_backorder,
            "is_in_stock": obj.is_in_stock,
            "low_stock": obj.is_low_stock(),
        }

    # def get_reviews(self, obj):
    #     return [
    #         {
    #             "user": review.user.email if review.user else review.ip_address,
    #             "rating": review.rating,
    #             "feedback": review.feedback,
    #         }
    #         for review in obj.reviews.all()
    #     ]

    def get_seo(self, obj):
        return {
            "title": obj.get_seo_title(),
            "description": obj.meta_description,
            "keywords": obj.meta_keywords,
        }

