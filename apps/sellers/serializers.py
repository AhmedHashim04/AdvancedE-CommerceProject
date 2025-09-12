from rest_framework import serializers
from .models import Seller, BankAccount, Payout
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


class BankAccountSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BankAccount
        fields = [
            "id", "seller", "account_holder_name", "bank_name",
            "iban", "swift_code", "created_at"
        ]
        read_only_fields = ["id", "seller", "created_at"]




class PayoutSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payout
        fields = [
            "id", "seller", "amount", "transaction_date", "reference_id"
        ]
        read_only_fields = ["id", "seller", "transaction_date", "reference_id"]
