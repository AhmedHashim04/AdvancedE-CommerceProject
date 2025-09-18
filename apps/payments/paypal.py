import requests

PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"  

PAYPAL_CLIENT_ID = "AXb4Hdv-QRhROm8EHyBipLxMpjFujccTmBZJtCW9H18aVGloOZQfijPpz6VVADnadKRP0oA9Geo-8BIm"
PAYPAL_CLIENT_SECRET = "EFDyEEwRMSHnhuL1oMLaJ46i1C8_hoNqVi24YwQAMq5np5uBNbxn1RIgm_Lx_9cgAMRsrhZthrNq1SDb"

class PayPalClient:
    def __init__(self):
        self.client_id = PAYPAL_CLIENT_ID
        self.secret = PAYPAL_CLIENT_SECRET
        self.base_url = PAYPAL_API_BASE

    def get_access_token(self):
        url = f"{self.base_url}/v1/oauth2/token"
        response = requests.post(
            url,
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.secret),
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def create_order(self, amount, currency="EGP"):
        url = f"{self.base_url}/v2/checkout/orders"
        access_token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {"currency_code": currency, "value": str(amount)}
                }

            ]
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def capture_order(self, order_id):
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        access_token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()
