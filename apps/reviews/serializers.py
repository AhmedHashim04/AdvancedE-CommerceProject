from .models import Review
from rest_framework import serializers


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    ip = serializers.CharField(read_only=True)
    product = serializers.StringRelatedField(read_only=True) 

    class Meta:
        model = Review
        fields = ["id", "product", "user", "ip", "feedback", "rating", "created_at"]
        read_only_fields = ["product", "user", "ip", "created_at"]
