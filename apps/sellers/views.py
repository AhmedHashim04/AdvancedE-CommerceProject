from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Seller
from apps.store.models import Product
from apps.sellers.serializers import SellerSerializer
from apps.store.serializers import ProductSerializer



class IsSellerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user



class SellerView(viewsets.ModelViewSet):
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOwner]

    def create(self, request, *args, **kwargs):
        if Seller.objects.filter(user=request.user).exists():
            return Response({"error": "You have already submitted a request."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({"status": "Request sent successfully. Please wait for approval."}, status=status.HTTP_201_CREATED)
    def list(self, request, *args, **kwargs):
        return Response({"error": "You cannot view this."}, status=status.HTTP_403_FORBIDDEN)
    
    def retrieve(self, request, *args, **kwargs):
        if Seller.objects.filter(user=request.user).exists():
            instance = Seller.objects.get(user=request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        if Seller.objects.filter(user=request.user).exists():
            instance = Seller.objects.get(user=request.user)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_verified = False
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Request updated successfully. Please wait for approval."}, status=status.HTTP_200_OK)
        return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        if Seller.objects.filter(user=request.user).exists():
            instance = Seller.objects.get(user=request.user)
            seller_products = Product.objects.filter(seller=instance).delete()
            instance.delete()
            return Response({"status": "all seller products and seller account deleted successfully ."}, status=status.HTTP_200_OK)
        return Response({"error": "You do not have a seller."}, status=status.HTTP_404_NOT_FOUND)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller__user=self.request.user)

    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)
