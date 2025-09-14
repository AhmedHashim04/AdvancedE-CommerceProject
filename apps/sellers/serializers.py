from rest_framework import serializers

from apps.shipping.models import ShippingCompany
from .models import Seller
from apps.store.models import Product
from apps.orders.models import Order


class SellerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Seller
        fields = [
            "id", "user", "store_name", "phone", "address",
            "is_verified", "created_at"
        ]
        read_only_fields = ["id", "user", "is_verified", "created_at"]

class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = "__all__"
        read_only_fields = ("user", "created_at", 'is_verified', "updated_at")
