from apps.store.models import Product
from apps.shipping.models import ShippingPlan
from decimal import Decimal

def _resolve_plan_key(plan_key):
    """The user's ShoppingCart stored plan keys in a non-serializable way in memory in your code.
    This helper attempts to resolve the plan object whether the key is already an instance
    or the id/str representation.
    """
    if isinstance(plan_key, ShippingPlan):
        return plan_key
    # if it's an int or numeric string, try to fetch
    try:
        plan_id = int(plan_key)
        return ShippingPlan.objects.get(id=plan_id)
    except Exception:
        # last-ditch: try to find by company name in key string (not robust)
        return None


def build_paypal_payload_from_cart(cart, currency="EGP"):
    """Return PayPal v2 payload dict built from the ShoppingCart instance.
    Each shipping plan becomes a purchase_unit. The consumer's currency is fixed to EGP.
    """
    purchase_units = []

    # guard: shipping might be empty or stored incorrectly
    shipping_map = getattr(cart, "shipping", {}) or {}

    # If shipping stored a placeholder 'address' key
    if shipping_map.get("address") == "No Address yet":
        raise ValueError("No shipping address provided")

    for plan_key, details in shipping_map.items():
        if plan_key == "address":
            raise ValueError("No shipping address provided")

        plan = _resolve_plan_key(plan_key)
        if plan is None:
            raise ValueError("Shipping plan error")

        items = []
        total_items_price = Decimal("0.00")
        shipping_cost = Decimal(str(details.get("base_price", "0.00")))

        # Fix: get weights dict
        weights = details.get("weights", {})
        for slug, weight_or_val in weights.items():
            try:
                product = Product.objects.get(slug=slug)
            except Product.DoesNotExist:
                continue

            cart_item = cart.cart.get(slug)
            if not cart_item:
                continue

            quantity = int(cart_item.get("quantity", 1))
            price = Decimal(cart_item.get("price", "0.00"))
            subtotal = price * quantity
            total_items_price += subtotal

            items.append({
                "name": product.name,
                "unit_amount": {"currency_code": currency, "value": str(price)},
                "quantity": str(quantity),
                "sku": getattr(product, "sku", str(product.id)),
                "category": "PHYSICAL_GOODS",
            })

        pu_amount = total_items_price + shipping_cost

        purchase_units.append({
            "reference_id": f"PLAN-{plan.id}",
            "description": f"Items shipped by {plan.company.name}",
            "amount": {
                "currency_code": currency,
                "value": str(pu_amount.quantize(Decimal("0.01"))),
                "breakdown": {
                    "item_total": {"currency_code": currency, "value": str(total_items_price.quantize(Decimal("0.01")))},
                    "shipping": {"currency_code": currency, "value": str(shipping_cost.quantize(Decimal("0.01")))},
                },
            },
            "items": items,
            # payee: expect each seller to have paypal_email attribute
            # We'll attach payee only if seller.paypal_email exists
            # Note: for marketplace split you might need more advanced PayPal product (Partner, Payouts, etc.)
        })

    payload = {
        "intent": "CAPTURE",
        "purchase_units": purchase_units,
        "application_context": {
            "brand_name": "SITE_NAME",
            # frontend will be given these return/cancel urls; DRF-only means frontend must handle them
            "return_url": "PAYPAL_RETURN_URL",
            "cancel_url": "PAYPAL_CANCEL_URL",
            "user_action": "PAY_NOW",
            "shipping_preference": "SET_PROVIDED_ADDRESS",
        }
    }

    return payload