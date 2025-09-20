from django.contrib import admin
from .models import Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("store_name", "user", "store_phone", "is_verified", "created_at")
    list_filter = ("is_verified", "created_at")
    search_fields = ("store_name", "user__username", "store_phone")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    actions = ["mark_verified"]

    @admin.action(description="Mark selected sellers as verified")
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} seller(s) marked as verified ✅")


