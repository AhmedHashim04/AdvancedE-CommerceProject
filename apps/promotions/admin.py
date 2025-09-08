from django.contrib import admin
from .models import Promotion, BQGPromotion

@admin.register(BQGPromotion)
class BQGPromotionAdmin(admin.ModelAdmin):
    list_display = ("gift", "quantity_to_buy", "gift_quantity", "percentage_amount", "fixed_amount")
    search_fields = ("gift__name",)
    list_filter = ("percentage_amount", "fixed_amount")

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "type", "is_active", "start_date", "end_date",
        "usage_count", "usage_limit", "percentage_amount", "fixed_amount", "bqg_promotion"
    )
    search_fields = ("id",)
    list_filter = ("type", "is_active", "start_date", "end_date")
    readonly_fields = ("usage_count",)
    autocomplete_fields = ["bqg_promotion"]