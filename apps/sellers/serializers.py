from rest_framework import serializers

from apps.shipping.models import ShippingCompany
from .models import Seller
from apps.shipping.serializers import AddressSerializer, ShippingCompanySerializer, ShippingPlanSerializer
from apps.promotions.models import Promotion , BQGPromotion

class SellerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    address = AddressSerializer()

    class Meta:
        model = Seller
        fields = "__all__"
        read_only_fields = ["id", "user",  "is_verified", "created_at"]

class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = "__all__"
        read_only_fields = ("user", "created_at", 'is_verified', "updated_at")

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"
        read_only_fields = ("seller", "created_at", "updated_at")