from rest_framework import serializers
from .models import Order, OrderItem

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
            "shipping_cost",
        ]
        read_only_fields = ["shipping_cost"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    address = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "ip_address",
            "address",
            "full_name",
            "notes",
            "status",
            "payment_method",
            "shipping_method",
            "shipping_cost",
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