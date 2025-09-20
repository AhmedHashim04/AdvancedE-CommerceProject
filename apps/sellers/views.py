from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Seller
from apps.store.models import Product
from apps.sellers.serializers import SellerSerializer, PromotionSellerSerializer, ProductSellerSerializer, SubOrderSerializer
from apps.promotions.models import Promotion
from apps.store.models import Brand, Category, Tag
from apps.store.serializers import BrandSerializer, CategorySerializer, TagSerializer

class IsSellerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOwner]

    def create(self, request, *args, **kwargs):
        if Seller.objects.filter(user=request.user).exists():
            return Response({"error": "You have already submitted a request."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, is_verified=False)
        return Response({"status": "Request sent successfully. Please wait for approval."}, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        return Response({"error": "You cannot view this."}, status=status.HTTP_403_FORBIDDEN)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Seller.objects.get(user=request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Seller.DoesNotExist:
            return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)
    def update(self, request, *args, **kwargs):
        try:
            instance = Seller.objects.get(user=request.user)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(is_verified=False)
            return Response({"status": "Request updated successfully. Please wait for approval."}, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)
    def destroy(self, request, *args, **kwargs):
        try:
            instance = Seller.objects.get(user=request.user)
            Product.objects.filter(seller=instance).delete()
            instance.delete()
            return Response({"status": "All seller products and seller account deleted successfully."}, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Returns the current user's seller profile.
        """
        try:
            instance = Seller.objects.get(user=request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Seller.DoesNotExist:
            return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSellerSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(seller__user=self.request.user)
    @action(detail=False, methods=['get'], url_path='orders')
    def orders(self, request):
        """
        Returns the current user's seller orders.
        """
        try:
            instance = Seller.objects.get(user=request.user)
            orders = instance.sub_orders.all()
            serializer = SubOrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Seller.DoesNotExist:
            return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)

class PromotionViewSet(viewsets.ModelViewSet):
    serializer_class = PromotionSellerSerializer
    permission_classes = [permissions.IsAuthenticated , IsSellerOwner]

    def get_queryset(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return Promotion.objects.filter(seller=seller)
    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)

class RequireBrandViewSet(viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOwner]
    def get_queryset(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return Brand.objects.filter(required_by=seller)
    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(required_by=seller, is_active=False)

class RequireCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOwner]
    def get_queryset(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return Category.objects.filter(required_by=seller)
    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(required_by=seller, is_active=False)

class RequireTagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOwner]
    def get_queryset(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return Tag.objects.filter(required_by=seller)
    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(required_by=seller, is_active=False)

