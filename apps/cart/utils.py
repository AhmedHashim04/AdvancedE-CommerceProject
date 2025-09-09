from .cart import ShoppingCart

def get_cart(request):
    return ShoppingCart(request)
