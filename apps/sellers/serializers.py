from rest_framework import serializers

from apps.shipping.models import ShippingCompany
from .models import Seller
from apps.shipping.serializers import AddressSerializer, ShippingCompanySerializer, ShippingPlanSerializer
from apps.store.models import Product
from apps.orders.models import Order


class SellerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    address = AddressSerializer()

    class Meta:
        model = Seller
        fields = [
        'default_shipping_company', 'store_name', 'store_description',
        'email', 'phone', 'address', 'on_delete', 'created_at',
        ]
        read_only_fields = ["id", "user", "is_verified", "created_at"]

class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = "__all__"
        read_only_fields = ("user", "created_at", 'is_verified', "updated_at")
