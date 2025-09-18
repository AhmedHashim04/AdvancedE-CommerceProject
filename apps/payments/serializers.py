

from rest_framework import serializers

class CartItemSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.CharField()
    subtotal = serializers.CharField()


class CheckoutSummarySerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    total_price = serializers.CharField()
    shipping_cost = serializers.CharField()

