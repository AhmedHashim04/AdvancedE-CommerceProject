from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Seller, BankAccount, TaxInfo, Payout
from apps.store.models import Product
from apps.orders.models import Order
from apps.sellers.serializers import (
    SellerSerializer, BankAccountSerializer, TaxInfoSerializer, 
    PayoutSerializer)
from apps.store.serializers import ProductSerializer
from apps.orders.serializers import OrderSerializer


class IsSellerOwner(permissions.BasePermission):
    """صلاحية: البائع لا يقدر يشوف غير نفسه"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class SellerViewSet(viewsets.ModelViewSet):
    """
    ViewSet للبائع (زي أمازون Seller Central)
    """
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOwner]

    def get_queryset(self):
        return Seller.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def products(self, request, pk=None):
        """جميع المنتجات الخاصة بالبائع"""
        seller = self.get_object()
        products = Product.objects.filter(seller=seller)
        return Response(ProductSerializer(products, many=True).data)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def orders(self, request, pk=None):
        """جميع الطلبات الخاصة بالبائع"""
        seller = self.get_object()
        orders = Order.objects.filter(seller=seller)
        return Response(OrderSerializer(orders, many=True).data)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def payouts(self, request, pk=None):
        """المدفوعات (فلوس أمازون للبائع)"""
        seller = self.get_object()
        payouts = Payout.objects.filter(seller=seller)
        return Response(PayoutSerializer(payouts, many=True).data)


class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(seller__user=self.request.user)

    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)


class TaxInfoViewSet(viewsets.ModelViewSet):
    serializer_class = TaxInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaxInfo.objects.filter(seller__user=self.request.user)

    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)


class ProductViewSet(viewsets.ModelViewSet):
    """البائع يتحكم في منتجاته"""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller__user=self.request.user)

    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """البائع يشوف الطلبات الخاصة به فقط"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(seller__user=self.request.user)


class PayoutViewSet(viewsets.ReadOnlyModelViewSet):
    """البائع يتابع مدفوعاته فقط"""
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payout.objects.filter(seller__user=self.request.user)
