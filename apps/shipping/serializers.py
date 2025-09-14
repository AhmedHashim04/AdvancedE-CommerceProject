
from rest_framework import serializers
from .models import Address, ShippingCompany, ShippingPlan

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ("user", "ip_address", "created_at", "updated_at")

class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class ShippingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingPlan
        fields = "__all__"
        read_only_fields = ("company", "created_at", "updated_at")

