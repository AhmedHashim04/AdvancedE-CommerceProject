from django.shortcuts import render

# Create your views here.
import requests

PAYMOB_URL = 'https://accept.paymob.com/api/acceptance/iframes/'

# API_KEY = 'ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TVRBMU16RXpOaXdpYm1GdFpTSTZJbWx1YVhScFlXd2lmUS5UbXNwbW9kbzllR2F0VU1ZbE9CMG9pSm9oelJ0M0VrTkRBNnNvM1N2Vk5pdUxRNDRzc1J6U0RiNnpBQUZjNWh3TUh4TXJHdFpOSzQxTnFyU0JMM1pNUQ=='
# PAYMOB_SECRET_KEY = 'egy_sk_test_59e67ba2608a45f6ebb30cee22f84ba952f825efbcc8a21916c7ee016c29c51c'
# PAYMOB_GENERAL_KEY = 'egy_pk_test_xUcW1vrEE8lwvSWzvi0oF02kUrWF1XHZ'


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
