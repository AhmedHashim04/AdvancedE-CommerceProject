from rest_framework.views import APIView
from rest_framework.response import Response
from paypal import PayPalClient

class PayPalCreateOrder(APIView):
    def post(self, request):
        amount = request.data.get("amount")  # ممكن تجيبه من cart
        paypal = PayPalClient()
        order = paypal.create_order(amount)
        return Response(order)

class PayPalCaptureOrder(APIView):
    def post(self, request):
        order_id = request.data.get("orderID")
        paypal = PayPalClient()
        capture = paypal.capture_order(order_id)
        return Response(capture)
