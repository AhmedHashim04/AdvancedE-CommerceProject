from django.contrib import admin
from .models import Seller, BankAccount, Payout 


class BankAccountInline(admin.StackedInline):
    model = BankAccount
    extra = 0
    can_delete = False



@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("store_name", "user", "phone", "is_verified", "created_at")
    list_filter = ("is_verified", "created_at")
    search_fields = ("store_name", "user__username", "phone")
    date_hierarchy = "created_at"
    inlines = [BankAccountInline]
    ordering = ("-created_at",)

    actions = ["mark_verified"]

    @admin.action(description="Mark selected sellers as verified")
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} seller(s) marked as verified ✅")


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("seller", "amount", "transaction_date", "reference_id")
    list_filter = ("transaction_date",)
    search_fields = ("seller__store_name", "reference_id")
    date_hierarchy = "transaction_date"
    ordering = ("-transaction_date",)


# في حالة لو حبيتهم منفصلين كمان
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("seller", "bank_name", "iban", "swift_code", "created_at")
    search_fields = ("seller__store_name", "iban", "bank_name")
    ordering = ("-created_at",)


