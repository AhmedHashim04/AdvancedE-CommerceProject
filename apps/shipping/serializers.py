
from rest_framework import serializers
from .models import Address, Governorate, City, ShippingCompany, ShippingPlan
from django.core.exceptions import ValidationError

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

# TODO Enhance Serializers
class AddressSerializer(serializers.ModelSerializer):
    # governorate = GovernorateSerializer()
    # city = CitySerializer()
    
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ("user", "ip_address", "created_at", "updated_at")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['governorate'] = GovernorateSerializer(instance.governorate).data
        representation['city'] = CitySerializer(instance.city).data
        return representation
    
class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

class ShippingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingPlan
        fields = "__all__"
        read_only_fields = ("company", "created_at", "updated_at", "is_active")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company'] = instance.company.company_name
        representation['governorates'] = [i.name_ar for i in instance.governorates.all()]
        return representation

    def validate(self, data):
        company = (
            data.get("company") 
            or getattr(self.instance, "company", None)
            or ShippingCompany.objects.filter(user=self.context["request"].user, is_verified=True).first()
        )
        estimated_days = data.get("estimated_days") or getattr(self.instance, "estimated_days", None)
        governorates = data.get("governorates") or []

        qs = ShippingPlan.objects.filter(
            company=company,
            estimated_days=estimated_days,
            is_active=True
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        conflict = qs.filter(governorates__in=governorates).distinct()
        if conflict.exists():
            gov_names = ", ".join(
                conflict.values_list("governorates__name_ar", flat=True)
            )
            raise serializers.ValidationError(
                f"A shipping plan for the same company with the same number of days already exists in the following governorates: {gov_names}"
            )

        return data
