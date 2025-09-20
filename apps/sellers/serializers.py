from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.shipping.models import ShippingCompany
from .models import Seller, SubOrder
from apps.shipping.serializers import AddressSerializer, ShippingCompanySerializer, ShippingPlanSerializer
from apps.promotions.models import Promotion, BQGPromotion, PromotionType
from apps.store.models import Product

class SubOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model= SubOrder
        fields = "__all__"

class SellerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    sub_orders = SubOrderSerializer(required=False, many=True)

    class Meta:
        model = Seller
        fields = "__all__"
        read_only_fields = ["id", "user", "sub_orders", "is_verified", "created_at"]
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # if instance.shipping_company:
        #     representation['shipping_company'] = instance.shipping_company.company_name
        # if instance.address:
        #     representation['address'] = AddressSerializer(instance.address).data
        return representation

class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = "__all__"
        read_only_fields = ("user", "created_at", 'is_verified', "updated_at")

class PromotionSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"
        read_only_fields = ("seller", "created_at", "updated_at")

    def create(self, validated_data):
        # Automatically set the seller to the logged-in user
        user = self.context['request'].user
        validated_data['seller'] = user.seller
        return super().create(validated_data)
    
    def validate(self, data):
        # Validate date logic
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        value = data.get('value')
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be later than end date.")

        # Validate discount logic based on type
        promo_type = data.get('type')
        print(value)

        if promo_type == PromotionType.PERCENTAGE and (value is None or not (0 < value <= 100)):
            raise serializers.ValidationError("Percentage amount must be between 0 and 100 for percentage type promotions.")
        if promo_type == PromotionType.FIXED and (value is None or value <= 0):
            raise serializers.ValidationError("Fixed amount must be greater than 0 for fixed type promotions.")
        # if promo_type == PromotionType.BUY_X_GET_Y:
        return data
class ProductSellerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields =["seller","slug","views_count","sales_count","rating","review_count","created_at","updated_at",]


    def validate_promotion(self, value):
        seller = self.context['request'].user.seller
        if value and value.seller != seller:
            raise serializers.ValidationError("Invalid promotion for this seller.")
        return value

    def validate_slug(self, value):
        if Product.objects.filter(slug=value).exists():
            raise serializers.ValidationError("هذا الـ slug مستخدم بالفعل، من فضلك اختر واحد مختلف.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.brand:
            representation['brand'] = instance.brand.name
        if instance.category:
            representation['category'] = instance.category.name
        if instance.tags:
            representation['tags'] = [tag.name for tag in instance.tags.all()]
        if instance.shipping_company:
            representation['shipping_company'] = instance.shipping_company.company_name
        if instance.promotion:
            representation['promotion'] = {
                "id": instance.promotion.id,
                "type": instance.promotion.type,
                "summary": instance.promotion.summary(1)  # Assuming bought_qty=1 for summary
            }
        return representation
    
    def create(self, validated_data):
        # Automatically set the seller to the logged-in user
        user = self.context['request'].user
        validated_data['seller'] = user.seller
        if validated_data.get("shipping_company")==None:
            validated_data["shipping_company"]=user.seller.default_shipping_company
        return super().create(validated_data)
    