from .models import Review
from rest_framework import serializers


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    ip_address = serializers.CharField(read_only=True)
    product = serializers.StringRelatedField(read_only=True) 

    class Meta:
        model = Review
        fields = ["id", "product", "user", "ip_address", "feedback", "rating", "created_at"]
        read_only_fields = ["product", "user", "ip_address", "created_at"]

