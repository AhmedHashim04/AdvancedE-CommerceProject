from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import  PermissionsMixin
import json
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from .utils import COUNTRY_CHOICES, CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    is_staff = models.BooleanField(_("staff status"),default=False,help_text=_("Designates whether the user can log into this admin site."),)
    is_active = models.BooleanField(_("active"),default=True,help_text=_("Designates whether this user should be treated as active. ""Unselect this instead of deleting accounts."),)
    verified = models.BooleanField(_("verified"), default=False, help_text=_("Designates whether this user has verified their email address."))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    email = models.EmailField(_("email address"), unique=True)
    address = models.ForeignKey("Address", verbose_name=_("Address"), on_delete=models.CASCADE, blank=True, null=True)
    wishlist = models.ManyToManyField("store.Product",verbose_name=_("Wishlist"),blank=True)

    def __str__(self):
        return self.email

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                             related_name='addresses',blank=True,null=True,verbose_name=_("User")) # for Guest checkout
    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"),help_text=_("Full Name"))
    phone_number = models.CharField(max_length=20,help_text=_("Primary Phone Number"), verbose_name=_("Phone Number"))
    alternate_phone = models.CharField(max_length=11,blank=True,help_text=_("Alternate Phone Number (optional)"),
                                       verbose_name=_("Alternate Phone Number (optional)"),)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES,help_text=_("Country"),verbose_name=_("Country"))
    state = models.CharField(max_length=100,help_text=_("State or City (optional)"),verbose_name=_("State or City"),blank=True, null=True)
    village = models.CharField(max_length=100,help_text=_("Village (optional)"),verbose_name=_("Village"),blank=True, null=True)
    address_line1 = models.CharField(max_length=255, verbose_name=_("Address Line 1"),help_text=_("Write detailed address that you want to deliver the order "))
    postal_code = models.CharField(max_length=20,help_text=_("you can leave it empty if you don't know what postal code"), verbose_name=_("Postal Code"))
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.address_line1}, {self.state}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UserActivityLog(models.Model):

    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view_product', 'View Product'),
        ('view_category', 'View Category'),
        ('search', 'Search'),
        ('filter', 'Filter'),
        ('compare', 'Compare'),
        ('share', 'Share'),
        ('add_to_cart', 'Add to Cart'),
        ('add_to_wishlist', 'Add to Wishlist'),
        ('view_cart', 'View Cart'),
        ('view_wishlist', 'View Wishlist'),
        ('coupon_applied', 'Coupon Applied'),
        ('coupon_removed', 'Coupon Removed'),
        ('add_address', 'Add Address'),
        ('edit_address', 'Edit Address'),
        ('delete_address', 'Delete Address'),
        ('set_default_address', 'Set Default Address'),
        ('checkout', 'Checkout'),
        ('order_placed', 'Order Placed'),
        ('order_cancelled', 'Order Cancelled'),
        ("review", "Review"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        return f"{user_str} - {self.action} @ {self.created_at}"

    def set_metadata(self, data: dict):
        """Helper لحفظ البيانات الإضافية بسهولة"""
        self.metadata = json.dumps(data)
        self.save()


