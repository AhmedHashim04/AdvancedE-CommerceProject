# from django.contrib import admin
# from django.urls import reverse
# from django.utils.html import format_html
# from django.utils.timezone import localtime
# from django.utils.translation import gettext_lazy as _
# from django.http import HttpResponse
# from .models import Order, OrderItem, OrderStatus, ShippingOption
# from project.admin import custom_admin_site

# from .utils import generate_invoice_pdf  # تأكد أن الفنكشن دي موجودة في utils.py

# admin.site.register(ShippingOption)
# custom_admin_site.register(ShippingOption)

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     fields = ("product", "quantity", "price", "discount", "total_price")
#     readonly_fields = ("total_price",)
#     extra = 0

#     @admin.display(description=_("Total Price"))
#     def total_price(self, obj):
#         return obj.total_item_price_after_discount

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "user_link",
#         "status",
#         "payment_method",
#         "total_price",
#         "created_at",
#         "invoice_link_en",
#         "invoice_link_ar",
#     )
#     list_filter = (
#         "full_name",
#         "status",
#         "governorate",
#         "payment_method",
#         "shipping_method",
#         "created_at",
#     )
#     search_fields = ("full_name", "id", "user__username", "user__email", "address_line")
#     readonly_fields = (
#         "total_price",
#         "created_at",
#         "updated_at",
#         "status_changed_at",
#         "invoice_download_links",
#     )
#     inlines = [OrderItemInline]
#     actions = ["mark_as_shipped", "mark_as_cancelled", "download_invoice_pdf_en", "download_invoice_pdf_ar"]

#     @admin.display(description=_("User"))
#     @admin.display(description=_("User"))
#     def user_link(self, obj):
#         if obj.user:
#             url = f"/admin/auth/user/{obj.user.pk}/change/"
#             return format_html('<a href="{}">{}</a>', url, obj.user.username)
#         return "-"

#     @admin.display(description=_("Invoice (EN)"))
#     def invoice_link_en(self, obj):
#         return format_html(
#             '<a class="button" href="{}">📄 EN</a>',
#             reverse("order:order-invoice-pdf", args=[obj.pk]) + "?lang=en"
#         )

#     @admin.display(description=_("Invoice (AR)"))
#     def invoice_link_ar(self, obj):
#         return format_html(
#             '<a class="button" href="{}">📄 AR</a>',
#             reverse("order:order-invoice-pdf", args=[obj.pk]) + "?lang=ar"
#         )

#     @admin.display(description=_("Invoice PDF"))
#     def invoice_download_links(self, obj):
#         return format_html(
#             '<a href="{}?lang=en">📥 Download English</a><br>'
#             '<a href="{}?lang=ar">📥 تحميل بالعربية</a>',
#             reverse("order:order-invoice-pdf", args=[obj.pk]),
#             reverse("order:order-invoice-pdf", args=[obj.pk])
#         )

#     def mark_as_shipped(self, request, queryset):
#         updated = queryset.update(
#             status=OrderStatus.SHIPPED, status_changed_at=localtime()
#         )
#         self.message_user(request, _("%d order(s) marked as shipped.") % updated)

#     def mark_as_cancelled(self, request, queryset):
#         updated = queryset.update(
#             status=OrderStatus.CANCELLED, status_changed_at=localtime()
#         )
#         self.message_user(request, _("%d order(s) marked as cancelled.") % updated)

#     def download_invoice_pdf_en(self, request, queryset):
#         for order in queryset:
#             pdf = generate_invoice_pdf(order, lang_code='en')
#             response = HttpResponse(pdf, content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}_en.pdf"'
#             return response

#     def download_invoice_pdf_ar(self, request, queryset):
#         for order in queryset:
#             pdf = generate_invoice_pdf(order, lang_code='ar')
#             response = HttpResponse(pdf, content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}_ar.pdf"'
#             return response

#     download_invoice_pdf_en.short_description = _("Download invoice (English)")
#     download_invoice_pdf_ar.short_description = _("Download invoice (Arabic)")

# custom_admin_site.register(Order, OrderAdmin)
