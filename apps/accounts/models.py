from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import  PermissionsMixin
import json
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from .utils import CustomUserManager
from core.utils import COUNTRY_CHOICES


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


