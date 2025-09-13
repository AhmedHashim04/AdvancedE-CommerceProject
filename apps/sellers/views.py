from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Seller
from apps.store.models import Product
from apps.orders.models import Order
from apps.sellers.serializers import SellerSerializer
from apps.store.serializers import ProductSerializer
from apps.orders.serializers import OrderSerializer


class IsSellerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOwner]

    def get_queryset(self):
        return Seller.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def products(self, request, pk=None):
        seller = self.get_object()
        products = Product.objects.filter(seller=seller)
        return Response(ProductSerializer(products, many=True).data)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller__user=self.request.user)

    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)

