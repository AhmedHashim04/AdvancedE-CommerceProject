from django.contrib import admin

from .models import Brand, Category, Product, ProductImage, ProductColor, Tag

from django.contrib import admin

from .models import Brand, Category, Product, ProductImage, ProductColor, Tag

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code")
    search_fields = ("name", "hex_code")

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("image", "alt_text")
    search_fields = ("alt_text",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "base_price", "stock_quantity", "promotion", "is_active", "is_featured")
    search_fields = ("name", "description", "brand__name", "category__name")
    list_filter = ("brand", "category", "is_active", "is_featured", "is_on_sale")
    autocomplete_fields = ["brand", "category", "tags", "color_options"]
    readonly_fields = ("views_count", "sales_count", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}