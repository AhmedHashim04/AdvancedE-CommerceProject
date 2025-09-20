
from rest_framework import serializers
from .models import Address, Governorate, City, ShippingCompany, ShippingPlan

class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Governorate
        fields = ["name_ar", "name_en"]
        read_only_fields = ("id", "governorate", "name_ar", "name_en", "code")

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields =  ["name_ar", "name_en"]
        read_only_fields = ("id", "city", "name_ar", "name_en", "code")


class AddressSerializer(serializers.ModelSerializer):
    governorate = GovernorateSerializer()
    city = CitySerializer()
    
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

