from .serializers import AddressSerializer, ShippingCompanySerializer, ShippingPlanSerializer
from .models import Address, ShippingCompany, ShippingPlan
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.utils import get_client_ip
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Address.objects.filter(user=user)
        ip = get_client_ip(self.request)
        return Address.objects.filter(ip_address=ip)

    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        if request.user.is_authenticated:
            if address.user == request.user:
                super().destroy(request, *args, **kwargs)
                return Response({"status": "Address deleted successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "You cannot delete this address"}, status=status.HTTP_403_FORBIDDEN)
        else:
            ip = get_client_ip(request)
            if address.ip_address == ip:
                super().destroy(request, *args, **kwargs)
                return Response({"status": "Address deleted successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "You cannot delete this address"}, status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            serializer.save(user=user)
        else:
            serializer.save(ip_address=get_client_ip(self.request))

    def perform_update(self, serializer):
        # Ensure only the owner (user or IP) can update
        address = self.get_object()
        user = self.request.user
        if user.is_authenticated:
            if address.user != user:
                raise PermissionError("You cannot update this address.")
            serializer.save(user=user)
        else:
            ip = get_client_ip(self.request)
            if address.ip_address != ip:
                raise PermissionError("You cannot update this address.")
            serializer.save(ip_address=ip)

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        address = self.get_object()
        user = request.user
        if user.is_authenticated:
            Address.objects.filter(user=user, is_default=True).exclude(pk=address.pk).update(is_default=False)
        else:
            ip = get_client_ip(request)
            Address.objects.filter(ip_address=ip, is_default=True).exclude(pk=address.pk).update(is_default=False)
        address.is_default = True
        address.save(update_fields=["is_default"])
        return Response({"status": "Now it's the default address"}, status=status.HTTP_200_OK)

class ShippingCompanyRequireView(viewsets.ModelViewSet):
    serializer_class = ShippingCompanySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if ShippingCompany.objects.filter(user=request.user).exists():
            return Response({"error": "You have already submitted a request."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({"status": "Request sent successfully. Please wait for approval."}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return Response({"error": "You cannot view this."}, status=status.HTTP_403_FORBIDDEN)
    
    def retrieve(self, request, *args, **kwargs):
        if ShippingCompany.objects.filter(user=request.user).exists():
            instance = ShippingCompany.objects.get(user=request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"error": "You do not have a shipping company."}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        if ShippingCompany.objects.filter(user=request.user).exists():
            instance = ShippingCompany.objects.get(user=request.user)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_verified = False
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "Request updated successfully. Please wait for approval."}, status=status.HTTP_200_OK)
        return Response({"error": "You do not have a shipping company."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        if ShippingCompany.objects.filter(user=request.user).exists():
            instance = ShippingCompany.objects.get(user=request.user)
            instance.delete()
            return Response({"status": "Shipping company deleted successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "You do not have a shipping company."}, status=status.HTTP_404_NOT_FOUND)

class ShippingPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShippingPlan.objects.filter(company__user=self.request.user, company__is_verified=True, is_active=True)
    
    def perform_create(self, serializer):
        company = ShippingCompany.objects.filter(user=self.request.user, is_verified=True).first()
        if not company:
            raise PermissionError("You must be a verified shipping company to create a shipping plan.")
        serializer.save(company=company)


"""
    Scenario of shipping cost calculation:
        customer add product if product.shipping_plan in cart_shipping_plans 
        calculate weight(add all shipping plans weights) if total_shipping_weight > plan.min_weight 
        calculate shipping_plan_weight_cost and change flag to true 
        and every product belong to this shipping plan calculate_shipping_plan_weight_costs again
        then calculate total shipping cost by sum all shipping_plan_costs + shipping_plan_weight_costs

    When removing a product
        
"""