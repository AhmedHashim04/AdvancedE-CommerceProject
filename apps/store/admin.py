from django.contrib import admin
# from django.utils.html import format_html
# from .models import Product, Brand, Category, Tag, ProductImage, ProductColor
# # from apps.orders.models import ShippingClass
from .models import Product
admin.site.register(Product)
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ("name", "brand", "category", "price", "stock_quantity", "is_in_stock", "thumbnail")
#     list_filter = ("brand", "category", "is_active", "is_featured")
#     search_fields = ("name", "sku", "barcode")
#     prepopulated_fields = {"slug": ("name",)}
#     readonly_fields = ("views_count", "sales_count","price")

#     def thumbnail(self, obj):
#         if obj.main_image:
#             return format_html(f'<img src="mediafiles/{obj.main_image}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />')

#         return "No Image"
#     thumbnail.short_description = "Image" 

#     def get_queryset(self, request):
#         """تحديد المنتجات ذات المخزون المنخفض"""
#         qs = super().get_queryset(request)
#         for product in qs:
#             if product.is_low_stock():
#                 product.name = f"⚠ {product.name}"
#         return qs

# admin.site.register(Brand)
# admin.site.register(Category)
# admin.site.register(Tag)
# admin.site.register(ProductImage)
# admin.site.register(ProductColor)
# # admin.site.register(ShippingClass)
