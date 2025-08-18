from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(
        'store.Product',
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Product"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("User"),
        help_text=_("The user who wrote the review"),
        blank=True,
        null=True  # for Guest user
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP Address"), blank=True, null=True
    )
    feedback = models.CharField(
        max_length=255,
        verbose_name=_("Review"),
        help_text=_("Write your feedback here"),
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES, default=3, verbose_name=_("Rating")
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ["-created_at"]

        constraints = [
            # يمنع يكرر الريفيو لو يوزر مسجل دخول
            UniqueConstraint(
                fields=["product", "user"],
                condition=Q(user__isnull=False),
                name="unique_product_review_user"
            ),
            # يمنع يكرر الريفيو لو ضيف (IP)
            UniqueConstraint(
                fields=["product", "ip_address"],
                condition=Q(user__isnull=True, ip_address__isnull=False),
                name="unique_product_review_ip"
            ),
        ]

    def __str__(self):
        identifier = self.user.email if self.user else self.ip_address
        return f"{identifier} - {self.product.name} ({self.rating}/5)"
