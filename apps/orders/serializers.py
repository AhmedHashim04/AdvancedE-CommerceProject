from rest_framework import serializers
from .models import Order, OrderItem
from apps.shipping.serializers import AddressSerializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price",
            "discount",
            "gift_item",
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "ip_address",
            "address",
            "notes",
            "status",
            "weight_cost",
            "total_price",
            "status_changed_at",
            "paid",
            "created_at",
            "updated_at",
            "invoice_pdf",
            "items",
        ]
        read_only_fields = [
            "id",
            "status_changed_at",
            "created_at",
            "updated_at",
            "shipping_cost",
            "weight_cost",
            "total_price",
            "invoice_pdf",
            "items",
        ]