from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from apps.store.models import Product
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from core.utils import get_client_ip

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
    
class ReviewDestroyView(APIView):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        product = get_object_or_404(Product, slug=slug)
        if self.request.user.is_authenticated:
            if Review.objects.filter(user=self.request.user, product=product).exists():
                Review.objects.filter(user=self.request.user, product=product).delete()
            else:
                return Response({"status": "you have not reviewed this product"})
        else:
            if Review.objects.filter(ip_address = get_client_ip(self.request), product=product).exists():
                Review.objects.filter(ip_address = get_client_ip(self.request), product=product).delete()
            else:
                return Response({"status": "you have not reviewed this product"})

        return Response({"status": "removed"})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
        

