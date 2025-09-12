from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.shipping.models import ShippingCompany, Address

class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_shipping_company = models.ForeignKey(ShippingCompany, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Default Shipping Company")
    store_name = models.CharField(max_length=150, unique=True)
    store_description = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.ForeignKey(Address, verbose_name=_("Address"), on_delete=models.CASCADE, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Seller")
        verbose_name_plural = _("Sellers")

    def __str__(self):
        return self.store_name

class BankAccount(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name="bank_account")
    account_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    iban = models.CharField(max_length=34, unique=True)
    swift_code = models.CharField(max_length=11, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")

    def __str__(self):
        return f"{self.bank_name} - {self.iban}"


class Payout(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="payouts")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _("Payout")
        verbose_name_plural = _("Payouts")

    def __str__(self):
        return f"{self.seller.store_name} - {self.amount}"
