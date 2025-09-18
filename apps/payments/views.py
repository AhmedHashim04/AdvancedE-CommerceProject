from rest_framework.views import APIView
from rest_framework.response import Response
from paypal import PayPalClient
from .serializers import CheckoutSummarySerializer
from decimal import Decimal
import requests

from rest_framework.permissions import AllowAny
from apps.cart.cart import ShoppingCart
from .utils import build_paypal_payload_from_cart
from rest_framework import status
from django.db import transaction
from apps.payments.models import Payment
from apps.shipping.models import Shipment, ShipmentItem, ShippingPlan
from apps.orders.models import Order as OrderModel, SubOrder
from apps.store.models import Product
from apps.shipping.models import Address

class CheckoutAPIView(APIView):
    """Return the built cart summary and a preview of PayPal payload.
    Frontend will call this to render checkout page.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # assume you attach ShoppingCart to request in middleware or instantiate here
        cart = ShoppingCart(request)
        summary = cart.get_cart_summary()
        serializer = CheckoutSummarySerializer(summary)

        # Build a preview payload but do not call PayPal yet
        try:
            payload = build_paypal_payload_from_cart(cart, currency="EGP")
        except Exception as exc:
            payload = {"error": str(exc)}

        return Response({"summary": serializer.data, "paypal_payload_preview": payload})


class CreatePayPalOrderAPIView(APIView):
    """Build the payload and call PayPal to create an Order. Return order id and approval link.
    Frontend will redirect user to the approval link.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        cart = ShoppingCart(request)
        if not cart.cart:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = build_paypal_payload_from_cart(cart, currency="EGP")
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        client = PayPalClient()
        try:
            paypal_resp = client.create_order(payload)
        except requests.HTTPError as exc:
            return Response({"detail": "PayPal error", "error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        # find approve link
        approve_url = None
        for link in paypal_resp.get("links", []):
            if link.get("rel") == "approve":
                approve_url = link.get("href")
                break

        # Save a temporary Payment record with paypal_order_id if you want to reconcile later.
        # We'll not create the final Order yet until capture succeeds.
        request.session["paypal_order_id"] = paypal_resp.get("id")
        request.session.modified = True

        return Response({"order_id": paypal_resp.get("id"), "approve_url": approve_url, "raw": paypal_resp})


class CapturePayPalOrderAPIView(APIView):
    """Called by frontend after PayPal approval redirect (frontend receives orderID).
    This endpoint captures the PayPal order and creates the real Order/SubOrders/Shipments in DB.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        order_id = request.data.get("orderID") or request.session.get("paypal_order_id")
        if not order_id:
            return Response({"detail": "orderID required"}, status=status.HTTP_400_BAD_REQUEST)

        client = PayPalClient()
        try:
            capture_resp = client.capture_order(order_id)
        except requests.HTTPError as exc:
            return Response({"detail": "PayPal capture failed", "error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        # Process capture response and persist Order
        try:
            with transaction.atomic():
                # Create Order
                cart = ShoppingCart(request)
                if not cart.cart:
                    return Response({"detail": "Cart empty"}, status=status.HTTP_400_BAD_REQUEST)

                # create top-level Order model
                order = OrderModel.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    address=getattr(request, "selected_address", None) or request.session.get("selected_address_id") and Address.objects.get(id=request.session.get("selected_address_id")),
                    total_price=Decimal(str(capture_resp.get("purchase_units", [{}])[0].get("payments", {}).get("captures", [{}])[0].get("amount", {}).get("value", "0.00"))),
                    paid=True,
                )

                # Save Payment record
                Payment.objects.create(
                    order=order,
                    paypal_order_id=order_id,
                    paypal_capture_id=None,
                    amount=Decimal(str(sum(Decimal(pu.get("payments", {}).get("captures", [{}])[0].get("amount", {}).get("value", "0.00")) for pu in capture_resp.get("purchase_units", [])))),
                    currency="EGP",
                    raw_response=capture_resp,
                )

                # For each purchase_unit create SubOrder + OrderItems + Shipment
                for pu in capture_resp.get("purchase_units", []):
                    ref = pu.get("reference_id")
                    # try to extract plan id
                    plan_id = None
                    if ref and ref.startswith("PLAN-"):
                        try:
                            plan_id = int(ref.split("-")[1])
                        except Exception:
                            plan_id = None

                    # Choose seller: we stored plan.company -> plan.company should have seller
                    plan = None
                    if plan_id:
                        try:
                            plan = ShippingPlan.objects.get(id=plan_id)
                        except ShippingPlan.DoesNotExist:
                            plan = None

                    seller = None
                    if plan:
                        # assume plan.company has a relation to seller; adapt to your data model
                        seller = getattr(plan.company, "seller", None)

                    sub_total = Decimal(str(pu.get("amount", {}).get("breakdown", {}).get("item_total", {}).get("value", "0.00")))
                    shipping_cost = Decimal(str(pu.get("amount", {}).get("breakdown", {}).get("shipping", {}).get("value", "0.00")))

                    suborder = SubOrder.objects.create(
                        order=order,
                        seller=seller,
                        subtotal=sub_total,
                        shipping_cost=shipping_cost,
                        status="paid",
                    )

                    # create Shipment for this SubOrder
                    shipment = Shipment.objects.create(
                        order=order,
                        seller=seller,
                        company=plan.company if plan else None,
                        shipping_plan=plan,
                        customer_address=order.address,
                        shipping_cost=shipping_cost,
                        status="pending",
                    )

                    # create OrderItems from items in purchase_unit
                    for item in pu.get("items", []):
                        sku = item.get("sku")
                        # attempt find product by sku then fallback to name
                        product = None
                        if sku:
                            try:
                                product = Product.objects.get(sku=sku)
                            except Product.DoesNotExist:
                                product = None

                        if not product:
                            try:
                                product = Product.objects.get(name=item.get("name"))
                            except Product.DoesNotExist:
                                product = None

                        quantity = int(item.get("quantity", "1"))
                        unit_price = Decimal(str(item.get("unit_amount", {}).get("value", "0.00")))

                        order_item = order.items.create(
                            product=product,
                            quantity=quantity,
                            price=unit_price,
                            discount=Decimal("0.00"),
                        )

                        # link to shipment
                        ShipmentItem.objects.create(
                            shipment=shipment,
                            order_item=order_item,
                            weight=Decimal("0.00"),
                        )

                # finally mark order paid and clear cart
                order.paid = True
                order.save()

                # clear cart
                cart.clear()

        except Exception as exc:
            transaction.set_rollback(True)
            return Response({"detail": "Failed to persist order", "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Payment captured and order created.", "paypal_capture": capture_resp})



# ---------------------
# 7) Settings you must add
# ---------------------
# PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_API_BASE (optional), PAYPAL_RETURN_URL, PAYPAL_CANCEL_URL
# SITE_NAME

# ---------------------
# NOTES & ADVICE
# ---------------------
# - This file is a single-file reference. Move code to the proper apps:
#   - services/paypal.py  -> PayPalClient
#   - apps.orders.models -> add SubOrder, Payment
#   - apps.orders.serializers -> serializers
#   - apps.orders.views -> the three APIViews
#   - apps.orders.urls -> urlpatterns
# - The ShoppingCart code in your session/cache may store ShippingPlan instances as keys; that's brittle.
#   It's better to store plan.id (int) or plan.pk as the key so session/cache serialization is stable.
# - I assumed certain relations (e.g., plan.company -> seller) which you must adapt to your real models.
# - PayPal in some regions might not accept EGP as a currency for direct checkout; if PayPal rejects EGP,
#   you must convert to a supported currency at checkout (or use PayPal's partner features). I didn't call the web
#   to check locale rules since you asked for code.
# - Frontend flow: frontend calls create-paypal-order -> receives approve_url -> redirect user to approve_url
#   After user approves, PayPal redirects to frontend return_url with orderID. Frontend then calls capture endpoint
#   with orderID to finalize and create the order in your DB.

# End of file