from django.shortcuts import render

# Create your views here.
import requests

PAYMOB_URL = 'https://accept.paymob.com/api/acceptance/iframes/'




def get_payment_token(amount, order_id):
    url = "https://accept.paymob.com/api/ecommerce/orders"
    headers = {"Authorization": f"Bearer {PAYMOB_SECRET_KEY}"}
    data = {
        "merchant_order_id": order_id,
        "amount_cents": amount * 100,  # Paymob يستخدم القروش
        "currency": "EGP",
        "delivery_needed": False,
        "items": []
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()["token"]

from django.http import JsonResponse

def payment_callback(request):

    return JsonResponse({'status': 'success'})
