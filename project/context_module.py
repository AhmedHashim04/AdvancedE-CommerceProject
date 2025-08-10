# from cart.cart import Cart as ShoppingCart
# from store.models import Category

# from django.core.cache import cache
# from accounts.models import Profile


def global_context(request):
    pass
#     context = {}

#     categories = cache.get('context_categories')
#     if categories is None:
#         categories = list(Category.objects.filter(parent=None).values_list('name', 'slug')[:10])
#         cache.set('context_categories', categories, 60 * 60 * 24)  # كاش يوم

#     cart = ShoppingCart(request)
#     cart_items_keys = cart.cart.keys()

#     profile = None
#     wishlist = None
    
#     if request.user.is_authenticated:
#         profile_cache_key = f"context_profile_{request.user.id}"
#         wishlist_cache_key = f"context_wishlist_{request.user.id}"

#         profile = cache.get(profile_cache_key)
#         wishlist = cache.get(wishlist_cache_key)

#         if profile is None:
#             try:
#                 profile = Profile.objects.select_related('user').get(user_id=request.user.id)
#                 cache.set(profile_cache_key, profile, 60 * 60 * 6)  #  6 h
#             except Profile.DoesNotExist:
#                 profile = None

#         if wishlist is None and profile is not None:
#             wishlist = list(profile.wishlist.values_list('slug', flat=True))
#             cache.set(wishlist_cache_key, wishlist, 60 * 60 * 2)  #  2 h

#         context["profile"] = profile
#         context["wishlist"] = wishlist

#     context.update({
#         "contextCategories": categories,
#         "cart_items_keys": cart_items_keys,
#         "total_cart_items": len(cart_items_keys),
#     })

#     return context
