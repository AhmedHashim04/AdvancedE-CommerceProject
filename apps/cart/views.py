from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import ListView, TemplateView
from store.models import Product
from .cart import Cart as ShoppingCart
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
# from django_ratelimit.decorators import ratelimit


# @ratelimit(key='ip', rate='100/m', method='POST', block=True)
@require_POST
def cart_add(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    referer_url = request.META.get("HTTP_REFERER", reverse("cart:cart_list"))

    if not url_has_allowed_host_and_scheme(referer_url, allowed_hosts={request.get_host()}):
        referer_url = reverse("cart:cart_list")
    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        message = _("Invalid quantity specified")
        if is_ajax:
            return JsonResponse({'success': False, 'message': message})
        return redirect(referer_url)
    if not product.available:
        message = _("%(name)s is currently unavailable") % {"name": product.name}
        if is_ajax:
            return JsonResponse({'success': False, 'message': message})
        return redirect(referer_url)
    cart.add(product=product, quantity=quantity)
    message = _("%(name)s added to cart successfully") % {"name": product.name}
    cart_count = len(cart.cart)
    if is_ajax:
        context = {
            'product': product,
            'cart_items_keys': cart.cart,
            'user': request.user
        }
        
        updated_htmls = {
            'cart_button': render_to_string('product/partials/cart_button.html', context, request=request),
            'new_cart_button': render_to_string('product/partials/new_cart_button.html', context, request=request),
        }

        return JsonResponse({
            'success': True,
            'message': message,
            'updated_htmls': updated_htmls,
            'product_slug': product.slug,
            'cart_count': cart_count
        })
    return redirect(referer_url)

# @ratelimit(key='ip', rate='20/m', method='POST', block=True)
@require_POST
def cart_update(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    referer_url = request.META.get("HTTP_REFERER", reverse("cart:cart_list"))

    if not url_has_allowed_host_and_scheme(
        referer_url, allowed_hosts={request.get_host()}
    ):
        referer_url = reverse("cart:cart_list")

    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity specified")
        return redirect(referer_url)

    if not (product.available):
        messages.warning(request, _("%(name)s is currently unavailable") % {"name": product.name})
        return redirect(referer_url)

    cart.add(product=product, quantity=quantity)
    messages.success(request, _("%(name)s updated in cart successfully") % {"name": product.name})
    return redirect(referer_url)

# @ratelimit(key='ip', rate='10/m', method='POST', block=True)
@require_POST
def cart_remove(request, slug):
    cart = ShoppingCart(request)
    product = get_object_or_404(Product, slug=slug)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    referer_url = request.META.get("HTTP_REFERER", reverse("cart:cart_list"))
    if not url_has_allowed_host_and_scheme(referer_url, allowed_hosts={request.get_host()}):
        referer_url = reverse("cart:cart_list")

    cart.remove(product)
    message = _("%(name)s removed from cart successfully") % {"name": product.name}
    cart_count = len(cart.cart)

    if is_ajax:
        context = {
            'product': product,
            'cart_items_keys': cart.cart,
            'user': request.user
        }

        updated_htmls = {
            'cart_button': render_to_string('product/partials/cart_button.html', context, request=request),
            'new_cart_button': render_to_string('product/partials/new_cart_button.html', context, request=request),
        }

        return JsonResponse({
            'success': True,
            'message': message,
            'updated_htmls': updated_htmls,
            'product_slug': product.slug,
            'cart_count': cart_count
        })
    return redirect(referer_url)

@require_POST
def cart_clear(request):
    cart = ShoppingCart(request)

    cart.clear()
    messages.success(request, "Cart cleared successfully")
    return redirect("cart:cart_list")

class CartView(ListView):

    template_name = "cart/cart.html"
    context_object_name = "cart"

    def get_queryset(self):
        return ShoppingCart(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = context["cart"]
        cart_summary = cart.get_cart_summary()

        context.update(
            {
                "cart_summary": cart_summary,
            }
        )
        return context

class CartContextMixin:
    def get_cart(self):
        try:
            return ShoppingCart(self.request)
        except Exception as e:
            # logger.exception("Error loading cart")
            messages.error(
                self.request, "An error occurred while loading the shopping cart."
            )
            return ShoppingCart(self.request)

    def get_cart_summary(self):
        return self.get_cart().get_cart_summary()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = self.get_cart()
        context["cart_summary"] = self.get_cart_summary()
        return context

class CartView(CartContextMixin, TemplateView):
    template_name = "cart/cart.html"
