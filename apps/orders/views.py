import logging
from decimal import Decimal
from io import BytesIO
from .utils import generate_invoice_pdf
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View
from store.models import Product
from cart.cart import Cart
from .forms import  OrderCreateForm
from .models import  Order, OrderItem, ShippingOption
from copy import deepcopy
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

# from django.utils.decorators import method_decorator
# from django_ratelimit.decorators import ratelimit
# from .tasks import send_order_emails_task, generate_invoice_task



    #     # # 3. 🚚 لمسؤول الشحن
    #     # subject_shipping = f"Shipping Info for Order #{order.id}"
    #     # message_shipping = render_to_string("order/order_shipping.html", context)
    #     # email_shipping = EmailMessage(
    #     #     subject_shipping,
    #     #     message_shipping,
    #     #     settings.DEFAULT_FROM_EMAIL,
    #     #     [settings.SHIPPING_EMAIL],  
    #     # )
    #     # email_shipping.content_subtype = "html"
    #     # email_shipping.send()


# @method_decorator(ratelimit(key='user', rate='20/m', block=True), name='dispatch')
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "order/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# @method_decorator(ratelimit(key='user', rate='20/m', block=True), name='dispatch')
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "order/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# @method_decorator(ratelimit(key='user', rate='100/m', block=True), name='dispatch') #2
class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderCreateForm
    template_name = "order/create_order.html"
    success_url = reverse_lazy("order:order_list")

    def form_valid(self, form):
        cart = Cart(self.request)
        if len(cart) == 0:
            form.add_error(None, "Your cart is empty.")
            return super().form_invalid(form)
        
        if not self.request.user.is_authenticated:

            cleaned_data = deepcopy(form.cleaned_data)
            if isinstance(cleaned_data.get('shipping_option'), ShippingOption):
                cleaned_data['shipping_option'] = cleaned_data['shipping_option'].pk

            self.request.session['order_form_data'] = cleaned_data
            self.request.session['product_slug'] = self.kwargs.get("slug")
            messages.info(self.request, _("Please log in to place your order."))
            return redirect(f'/accounts/google/login/?next={self.request.path}')

        try:
            with transaction.atomic():
                order = self._create_order_object(form, cart)
                self._create_order_items(order, cart)
                self.object = order

            # generate_invoice_task.delay(order.id)
            self._invoice_generation(order)
            self._cleanup_session(cart)
            messages.success(
                self.request,
                _("Your order has been placed successfully. "
                "Your invoice is being generated and will be available shortly."),
            )

        except Exception as e:
            # logger.exception("Order processing failed")
            form.add_error(None, _("Error processing your order: %(error)s") % {'error': str(e)})
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_initial(self):

        profile = getattr(self.request.user, 'profile', None)
        initial = {
        }
        if profile:
            initial.update({
                'full_name': self.request.user.get_full_name() or self.request.user.username,
                'governorate': profile.governorate,
                'phone': profile.phone,
            })
        return initial


    def _create_order_object(self, form, cart):
        order = form.save(commit=False)
        order.user = self.request.user
        order.shipping_cost = order.calculate_shipping_cost()

        order.shipping_option = form.cleaned_data['shipping_option']

        get_total_price_after_discount = cart.get_total_price_after_discount()
        order.total_price = max(
            (get_total_price_after_discount + order.shipping_cost+order.weight_cost()).quantize(Decimal("0.01")),
            Decimal("0.00"),
        )
        order.save()
        return order

    def _create_order_items(self, order, cart):
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["price"],
                discount=item["discount"],
            )

    def _invoice_generation(self, order):
        pdf_content = generate_invoice_pdf(self.request,order,self.request.LANGUAGE_CODE)
        if pdf_content:
            order.invoice_pdf.save(f"invoice_{order.id}.pdf", ContentFile(pdf_content))
            order.save()
            # send_order_emails_task.delay(order.id)
            self._send_emails(order)

    def _cleanup_session(self, cart):
        """Clean session data after successful order"""
        cart.clear()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        if "form" not in context:
            context["form"] = self.get_form()
        return context

    def get_form(self, form_class=None):
        
        form_class = form_class or self.get_form_class()
        if self.request.method == "POST":
            return form_class(self.request.POST, user=self.request.user)
        return form_class(user=self.request.user, initial=self.get_initial())


    def _send_emails(self, order):
        context = {
            'order': order,
            'user': order.user,
            'shipping_address': f'{order.governorate}-{order.city}-{order.address_line}',
            'shipping_cost': order.shipping_option,
            'total': order.total_price,
        }

        # 1. 📤 للعميل
        subject_customer = f"Thanks for your order #{order.id}"
        message_customer = render_to_string("order/order_customer.html", context)
        email_customer = EmailMessage(
            subject_customer,
            message_customer,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
        )
        if order.invoice_pdf:
            email_customer.attach_file(order.invoice_pdf.path)
        email_customer.content_subtype = "html"
        email_customer.send()

        # 2. 🛒 لصاحب المتجر
        subject_owner = f"New Order #{order.id} placed"
        message_owner = render_to_string("order/order_store_owner.html", context)
        email_owner = EmailMessage(
            subject_owner,
            message_owner,
            settings.DEFAULT_FROM_EMAIL,
            [settings.STORE_OWNER_EMAIL],  
        )
        if order.invoice_pdf:
            email_owner.attach_file(order.invoice_pdf.path)
        email_owner.content_subtype = "html"
        email_owner.send()


# @method_decorator(ratelimit(key='user', rate='300/m', block=True), name='dispatch')
class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = Order.objects.filter(pk=pk, user=request.user).first()
        if order and hasattr(order, "status"):
            order.update_status("cancelled")
        return HttpResponseRedirect(reverse("order:order_detail", args=[order.pk]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.object
        return context

class OrderNowCreateView(CreateView):
    model = Order
    form_class = OrderCreateForm
    template_name = "order/create_order.html"
    success_url = reverse_lazy("order:order_list")

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get("slug") or request.session.pop("product_slug", None)
        self.product = get_object_or_404(Product, slug=slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.request.user.is_authenticated:

            cleaned_data = deepcopy(form.cleaned_data)
            if isinstance(cleaned_data.get('shipping_option'), ShippingOption):
                cleaned_data['shipping_option'] = cleaned_data['shipping_option'].pk

            self.request.session['order_form_data'] = cleaned_data
            self.request.session['product_slug'] = self.kwargs.get("slug")
            messages.info(self.request, _("Please log in to place your order."))
            return redirect(f'/accounts/google/login/?next={self.request.path}')
        
        if not self.product:
            form.add_error(None, "There is no product.")
            return super().form_invalid(form)

        try:
            with transaction.atomic():
                order = self._create_order_object(form)
                self._create_order_items(order)
                self.object = order
                
            # generate_invoice_task.delay(order.id)
            self._invoice_generation(order)
            messages.success(
                self.request,
                _("Your order has been placed successfully. "
                  "Your invoice is being generated and will be available shortly."),
            )

        except Exception as e:
            form.add_error(None, _("Error processing your order: %(error)s") % {'error': str(e)})
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()

        # تعبئة بيانات البروفايل إن وجدت
        if self.request.user.is_authenticated:
            profile = getattr(self.request.user, 'profile', None)
            initial.update({
                'full_name': self.request.user.get_full_name() or self.request.user.username,            
            })
            if profile:
                initial.update({
                    'governorate': profile.governorate,
                    'phone': profile.phone,
                })

        session_data = self.request.session.pop('order_form_data', None)
        if session_data:
            initial.update(session_data)

        return initial

    def _create_order_object(self, form):
        order = form.save(commit=False)
        order.user = self.request.user
        order.shipping_cost = order.calculate_shipping_cost()
        order.shipping_option = form.cleaned_data['shipping_option']

        total_price = self.product.price_after_discount + order.shipping_cost
        order.total_price = max(total_price.quantize(Decimal("0.01")), Decimal("0.00"))

        order.save()
        return order

    def _create_order_items(self, order):
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price,
            discount=self.product.discount,
        )

    def _invoice_generation(self, order):
        pdf_content = generate_invoice_pdf(self.request,order,self.request.LANGUAGE_CODE)
        if pdf_content:
            order.invoice_pdf.save(f"invoice_{order.id}.pdf", ContentFile(pdf_content))
            order.save()
            # send_order_emails_task.delay(order.id)
            self._send_emails(order)
            messages.success(
                self.request,
                _("Your invoice had been generated and available in your mailbox.check your Gmail."),
            )




    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        if self.request.method == "POST":
            return form_class(self.request.POST, user=self.request.user)
        return form_class(user=self.request.user, initial=self.get_initial())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.product
        context["order_now"] = True
        
        if "form" not in context:
            context["form"] = self.get_form()
        return context

    def _send_emails(self, order):
        context = {
            'order': order,
            'user': order.user,
            'shipping_address': f'{order.governorate}-{order.city}-{order.address_line}',
            'shipping_cost': order.shipping_option,
            'total': order.total_price,
            
        }

        # 1. 📤 للعميل
        subject_customer = f"Thanks for your order #{order.id}"
        message_customer = render_to_string("order/order_customer.html", context)
        email_customer = EmailMessage(
            subject_customer,
            message_customer,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
        )
        if order.invoice_pdf:
            email_customer.attach_file(order.invoice_pdf.path)
        email_customer.content_subtype = "html"
        email_customer.send()

        # 2. 🛒 لصاحب المتجر
        subject_owner = f"New Order #{order.id} placed"
        message_owner = render_to_string("order/order_store_owner.html", context)
        email_owner = EmailMessage(
            subject_owner,
            message_owner,
            settings.DEFAULT_FROM_EMAIL,
            [settings.STORE_OWNER_EMAIL],  
        )
        if order.invoice_pdf:
            email_owner.attach_file(order.invoice_pdf.path)
        email_owner.content_subtype = "html"
        email_owner.send()

