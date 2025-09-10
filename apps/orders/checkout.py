from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal
from apps.cart.cart import ShoppingCart
from apps.orders.models import Order, OrderItem, OrderStatus, ShippingClass
from apps.store.models import Product
    

class CheckoutCreateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        cart = ShoppingCart(request)

        if not cart.cart:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        address_id = data.get("address")
        # shipping_method = data.get("shipping_method", ShippingClass.STANDARD)
        notes = data.get("notes", "")

        try:
            address = request.user.addresses.get(pk=address_id)
        except Exception:
            return Response({"detail": "Invalid address."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                ip_address=request.META.get("REMOTE_ADDR"),
                address=address,
                full_name=f"{address.first_name} {address.last_name}",
                notes=notes,
                # shipping_method=shipping_method,
                status=OrderStatus.PENDING,
                total_price=0,
            )

            total_price = Decimal("0.00")

            # 2. إنشاء OrderItems
            for slug, item in cart.cart.items():
                try:
                    product = Product.objects.get(slug=slug)
                except Product.DoesNotExist:
                    continue

                quantity = int(item["quantity"])
                price = Decimal(item["price"])
                discount = Decimal("0.00")

                # لو في promotion
                if item.get("promotion") and item["promotion"] != "disactivated":
                    promo_data = item["promotion"]
                    if promo_data.get("type") in ["BQG"]:
                        gift_item = promo_data.get("gift")
                        gift_quantity = promo_data.get("gift_quantity", 0)
                        unit_gift_price = promo_data.get("unit_gift_price", 0)
                        discount_gift_price = unit_gift_price - promo_data.get("discounted_gift_price", 0)

                        order_item = OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=price,
                            discount=discount,
                        )


                        gift_item = OrderItem.objects.create(
                            order=order,
                            product=gift_item,
                            quantity=gift_quantity,
                            price=unit_gift_price,
                            discount=discount_gift_price * gift_quantity,
                            gift_item=True
                        )

                        total_gift_price = (unit_gift_price - discount_gift_price) * gift_quantity
                        total_price += total_gift_price

                total_price += (price * quantity) - discount
                
            # 3. حساب الشحن
            # order.calculate_shipping()
            # total_price += order.shipping_cost

            order.total_price = total_price
            order.save()

            # 4. تفريغ الكارت
            cart.clear()

        return Response({
            "order_id": str(order.id),
            "status": order.status,
            "total_price": str(order.total_price),
            # "shipping_cost": str(order.shipping_cost),
            "created_at": order.created_at,
        }, status=status.HTTP_201_CREATED)
