from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from apps.store.models import Product
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from core.utils import get_client_ip
from core.utils import EmptySerializer


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        product = get_object_or_404(Product, slug=slug)
        if self.request.user.is_authenticated:
            if Review.objects.filter(user=self.request.user, product=product).exists():
                return Response({"You have already reviewed this product"})
        else:
            if Review.objects.filter(ip_address = get_client_ip(self.request), product=product).exists():
                return Response("You have already reviewed this product")

        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        slug = self.kwargs.get("slug")
        product = get_object_or_404(Product, slug=slug)

        if self.request.user.is_authenticated:
            if Review.objects.filter(user=self.request.user, product=product).exists():
                return Response({"You have already reviewed this product"})
            serializer.save(user=self.request.user, product=product)
        else:
            if Review.objects.filter(ip_address = get_client_ip(self.request), product=product).exists():
                return Response("You have already reviewed this product")
            serializer.save(ip_address = get_client_ip(self.request), product=product)
    
class ReviewDestroyView(generics.DestroyAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.AllowAny]
    def get_object(self):
        slug = self.kwargs.get("slug")
        product = get_object_or_404(Product, slug=slug)
        if self.request.user.is_authenticated:
            review = Review.objects.filter(user=self.request.user, product=product).first()
            if not review:
                raise NotFound(detail="You have not reviewed this product")
            return review
        review = Review.objects.filter(ip_address=get_client_ip(self.request), product=product).first()
        if not review:
            raise NotFound(detail="You have not reviewed this product")
        return review

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({"status": "removed"})

class ReviewUpdateView(generics.UpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        slug = self.kwargs.get("slug")
        product = get_object_or_404(Product, slug=slug)
        if self.request.user.is_authenticated:
            review = Review.objects.filter(user=self.request.user, product=product).first()
            if not review:
                raise NotFound(detail="You have not reviewed this product")
            return review
        review = Review.objects.filter(ip_address=get_client_ip(self.request), product=product).first()
        if not review:
            raise NotFound(detail="You have not reviewed this product")
        return review

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
