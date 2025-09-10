from apps.orders.serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework import  permissions, status
from core.utils import get_client_ip
from django.db import transaction
from decimal import Decimal
from apps.cart.cart import ShoppingCart
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.store.models import Product
from apps.accounts.models import Address

class OrderCreateView(CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def _has_active_promotion(self, item):
        if item.get("promotion") and item["promotion"] != "disactivated":
            promo_data = item["promotion"]
            if promo_data and hasattr(promo_data, "type") and \
                    promo_data.get("can_apply") is True and \
                    promo_data.get("type") in ["BQG"]:
                return promo_data
        return None

    def _get_or_create_address(self, request, data):
        """
        - If user is authenticated → return address from user's addresses.
        - If guest:
            * If address_id is provided and exists for the IP → return it.
            * If address_id is missing or invalid → create a new Address from request data.
        """
        address_id = data.get("address")
        if request.user.is_authenticated:
            return request.user.addresses.filter(pk=address_id).first()

        client_ip = get_client_ip(request)

        if address_id:
            address = Address.objects.filter(pk=address_id, user=None, ip_address=client_ip).first()
            if address:
                return address

        # create new guest address
        return Address.objects.create(
            ip_address=client_ip,
            full_name=data.get("full_name"),
            phone_number=data.get("phone_number"),
            alternate_phone=data.get("alternate_phone"),
            country=data.get("country"),
            state=data.get("state"),
            village=data.get("village"),
            address_line1=data.get("address_line1"),
            postal_code=data.get("postal_code", ""),
            is_default=False,
        )

    def create(self, request, *args, **kwargs):
        cart = ShoppingCart(request)

        if not cart.cart:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        notes = data.get("notes", "")

        address = self._get_or_create_address(request, data)
        if not address:
            return Response({"detail": "Invalid address."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if request.user.is_authenticated:
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    notes=notes,
                    status=OrderStatus.PENDING,
                    total_price=0,
                )
            else:
                order = Order.objects.create(
                    ip_address=get_client_ip(request),
                    address=address,
                    notes=notes,
                    status=OrderStatus.PENDING,
                    total_price=0,
                )

            total_price = Decimal("0.00")

            for slug, item in cart.cart.items():
                try:
                    product = Product.objects.get(slug=slug)
                except Product.DoesNotExist:
                    continue

                quantity = int(item["quantity"])
                price = Decimal(item["price"])
                discount = Decimal("0.00")

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    discount=discount,
                )
                total_price += (price * quantity) - discount

                # promotions
                if promo_data := self._has_active_promotion(item):
                    gift_item = promo_data.get("gift")
                    unit_gift_price = promo_data.get("unit_gift_price", 0)
                    gift_quantity = promo_data.get("gift_quantity", 0)
                    discount_gift_price = unit_gift_price - promo_data.get("discounted_gift_price", 0)

                    OrderItem.objects.create(
                        order=order,
                        product=gift_item,
                        quantity=gift_quantity,
                        price=unit_gift_price,
                        discount=discount_gift_price * gift_quantity,
                        gift_item=True
                    )

                    total_price += (unit_gift_price - discount_gift_price) * gift_quantity

            order.total_price = total_price
            order.save()
            cart.clear()

        return Response({
            "order_id": str(order.id),
            "status": order.status,
            "total_price": str(order.total_price),
            "created_at": order.created_at,
        }, status=status.HTTP_201_CREATED)

class OrderListView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.filter(ip_address=get_client_ip(self.request))
    
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.filter(ip_address=get_client_ip(self.request))

class OrderCancelView(DestroyAPIView):
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.filter(ip_address=get_client_ip(self.request))
