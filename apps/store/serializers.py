from apps.reviews.serializers import ReviewSerializer

from rest_framework import serializers
from apps.store.models import (
    Product, Brand, Category, Tag, ProductColor, ProductImage
)
from apps.promotions.models import Promotion


# --------------------------
# Utility: Dynamic Fields
# --------------------------
class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.context.get("fields", None)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# --------------------------
# Related Mini Serializers
# --------------------------
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


# --------------------------
# Promotion Serializer
# --------------------------
class PromotionSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = ["id", "type", "summary"]

    def get_summary(self, obj):
        bought_qty = self.context.get("bought_qty", 1)
        return obj.summary(bought_qty)


# --------------------------
# Product Serializer
# --------------------------
class ProductSerializer(DynamicFieldsModelSerializer):
    brand = BrandMiniSerializer(read_only=True)
    category = CategoryMiniSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    color_options = ProductColorSerializer(many=True, read_only=True)
    gallery = ProductImageSerializer(many=True, read_only=True)
    promotion = PromotionSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    pricing = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "short_description", "description",
            "sku", "barcode", "promotion", "pricing",
            "brand", "category", "tags", "color_options",
            "stock",  "main_image", "gallery",
            "video_url", "view_360_url", "weight", "width", "height", "depth",
            "has_variants", "attributes", "is_featured",
            "rating", "review_count", "views_count", "sales_count",
            "meta_title", "meta_description", "meta_keywords", "seo",
            "created_at", "updated_at", "reviews"
        ]
        read_only_fields = fields

    # ---------- Custom Methods ----------
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

    def get_seo(self, obj):
        return {
            "title": obj.get_seo_title(),
            "description": obj.meta_description,
            "keywords": obj.meta_keywords,
        }
