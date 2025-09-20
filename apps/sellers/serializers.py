from rest_framework import serializers

from apps.shipping.models import ShippingCompany
from .models import Seller, SubOrder
from apps.shipping.serializers import AddressSerializer, ShippingCompanySerializer, ShippingPlanSerializer
from apps.promotions.models import Promotion , BQGPromotion

class SubOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model= SubOrder
        fields = "__all__"

# TODO enhance serializers
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

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"
        read_only_fields = ("seller", "created_at", "updated_at")