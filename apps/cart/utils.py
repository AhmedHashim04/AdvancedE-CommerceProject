
from .SRP_cart import CartManager, CartStorage, CartCalculator, PromotionService

def get_cart(request):
    storage = CartStorage()
    calculator = CartCalculator()
    promo_service = PromotionService()
    return CartManager(request, storage, calculator, promo_service)
