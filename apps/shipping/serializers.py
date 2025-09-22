
from rest_framework import serializers
from .models import Address, Governorate, City, ShippingCompany, ShippingPlan, WeightPricing
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

    # def create(self, validated_data):
    #     if validated_data.get('is_default', False):
    #         Address.objects.filter(user=user, is_default=True).update(is_default=False)
    #     return super().create(validated_data)
    
class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.company_address:
            representation['company_address'] = AddressSerializer(instance.company_address).data
        return representation

class WeightPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightPricing
        fields = ["min_weight", "price_per_kilo"]


class ShippingPlanSerializer(serializers.ModelSerializer):
    # input: IDs فقط
    governorates = serializers.PrimaryKeyRelatedField(
        queryset=Governorate.objects.all(),
        many=True
    )

    # output: تفاصيل كاملة
    company_detail = ShippingCompanySerializer(source="company", read_only=True)
    governorates_detail = GovernorateSerializer(source="governorates", many=True, read_only=True)
    weight_pricing = WeightPricingSerializer(required=False)

    class Meta:
        model = ShippingPlan
        fields = [
            "id",
            "governorates",
            "base_price",
            "estimated_days",
            "is_active",
            "company_detail",
            "governorates_detail",
            "weight_pricing",
        ]

    def create(self, validated_data):
        # شيل weight_pricing من البيانات
        weight_pricing_data = validated_data.pop("weight_pricing", None)
        plan = super().create(validated_data)

        # أنشئ WeightPricing لو موجود
        if weight_pricing_data:
            WeightPricing.objects.create(plan=plan, **weight_pricing_data)

        return plan

    def update(self, instance, validated_data):
        # شيل weight_pricing من البيانات
        weight_pricing_data = validated_data.pop("weight_pricing", None)
        plan = super().update(instance, validated_data)

        # عدّل أو أنشئ WeightPricing
        if weight_pricing_data:
            WeightPricing.objects.update_or_create(plan=plan, defaults=weight_pricing_data)

        return plan
    def validate(self, data):
        request = self.context["request"]

        company = (
            getattr(self.instance, "company", None)
            or ShippingCompany.objects.filter(user=request.user, is_verified=True).first()
        )
        estimated_days = data.get("estimated_days") or getattr(self.instance, "estimated_days", None)

        if "governorates" in data:
            governorates = data["governorates"]
        elif self.instance:
            governorates = self.instance.governorates.all()
        else:
            governorates = []

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
                conflict.values_list("governorates__name_ar", flat=True).distinct()
            )
            raise serializers.ValidationError({
                "governorates": f"A shipping plan for the same company and the same number of days already exists in the following governorates: {gov_names}"
            })

        return data
