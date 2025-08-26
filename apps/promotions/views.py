from apps.promotions.models import Promotion
from cart.cart import Cart

def apply_cart_promotions(item):
    cart = Cart()
    if item.product.promotion.discount_type == Promotion.DiscountType.GIFT:
        gift = item.product.promotion.gift_product
        cart.add(None, 1, gift)
    if item.product.promotion.discount_type == Promotion.DiscountType.BXGY:
        if cart.cart.get(item.product.id, {}).get("quantity", 0) >= item.product.promotion.buy_quantity:
            quantity_gift = item.product.promotion.get_quantity
            cart.add(None, quantity_gift, item.product)