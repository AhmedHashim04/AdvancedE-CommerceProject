from decimal import Decimal
from django.conf import settings
# from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models, transaction
from django.db.models import Avg, UniqueConstraint
# from django.db.models.signals import post_delete, post_save
# from django.dispatch import receiver
from django.urls import reverse
# from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# from .utils import generate_product_slug, generate_category_slug
from django.utils.functional import cached_property
# from PIL import Image
# from django.contrib.auth import get_user_model
# from io import BytesIO
# from django.core.files.base import ContentFile
# import os

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
    # category = models.ForeignKey("Category", on_delete=models.SET_NULL, verbose_name=_("Category"),
    #                              blank=True, null=True, related_name="products")
    description = models.TextField(max_length=1000, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Price"),
                                 validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to="products/", verbose_name=_("Product Image"), blank=True, null=True)
    overall_rating = models.FloatField(default=5.0, verbose_name=_("Overall Rating"))
    available = models.BooleanField(default=True, verbose_name=_("Is Available"))
    trending = models.BooleanField(default=False, verbose_name=_("Trending"),
                                   help_text=_("Is this product trending?"))
    in_random_list = models.BooleanField(default=False, verbose_name=_("Random"))
    
    # tags = models.ManyToManyField("Tag", verbose_name=_("Tags"), blank=True, related_name="products")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,default=1,related_name="products")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=["price"], name="price_idx"),
            models.Index(fields=['overall_rating','available']),
            # models.Index(fields=['discount','available']),
            models.Index(fields=['created_at','available']),
            models.Index(fields=["-overall_rating"], name="rating_idx"),
            models.Index(fields=["available"], name="available_idx"),
            models.Index(fields=["trending","available"], name="available_trending_idx"),
            models.Index(fields=["in_random_list","available"], name="random_trending_idx"),
            models.Index(fields=["created_at"]),
            # models.Index(fields=["discount"]),
        ]

    def __str__(self):
        status = _("Available") if self.available else _("Not available")
        return f"{self.name} - {self.price} EGP - {status}"

    # def get_absolute_url(self):
    #     return reverse("product:product_detail", kwargs={"slug": self.slug})

    # @cached_property
    # def price_after_discount(self):
    #     return (
    #         self.price
    #         * (Decimal(100) - self.discount)
    #         / Decimal(100).quantize(Decimal(".01"))
    #     )

    # def update_rating(self):
    #     result = self.reviews.aggregate(average_rating=Avg("rating"))  # Pyright: ignore
    #     self.overall_rating = round(result["average_rating"] or 0, 2)
    #     self.save(update_fields=["overall_rating"])


    # def save(self, *args, **kwargs):
    #     # self.owner = self.request.user

    #     # حذف الصورة القديمة لو فيه تحديث
    #     if self.pk:
    #         old_instance = Product.objects.filter(pk=self.pk).first()
    #         if old_instance and old_instance.image and self.image != old_instance.image:
    #             old_image_path = old_instance.image.path
    #             if os.path.isfile(old_image_path):
    #                 os.remove(old_image_path)

    #     # توليد slug لو مفيش
    #     if not self.pk and not self.slug:
    #         self.slug = generate_product_slug(self.name)

    #     # تحويل الصورة إلى webp
    #     if self.image:
    #         ext = os.path.splitext(self.image.name)[1].lower()
    #         if ext != ".webp": 
    #             img = Image.open(self.image)
    #             img = img.convert("RGB")
    #             img.thumbnail((800, 800))  # Resize

    #             buffer = BytesIO()
    #             img.save(buffer, format="WEBP", optimize=True, quality=75)

    #             name_without_ext = self.image.name.rsplit(".", 1)[0]
    #             final_name = f"{name_without_ext}.webp"

    #             self.image.save(final_name, ContentFile(buffer.getvalue()), save=False)


    #     try:
    #         with transaction.atomic():
    #             super().save(*args, **kwargs)
    #     except IntegrityError:
    #         self.slug = generate_product_slug(f"{self.name}-{timezone.now().timestamp()}")
    #         with transaction.atomic():
    #             super().save(*args, **kwargs)

# class Review(models.Model):
#     RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="reviews",
#         verbose_name=_("Product"),
#     )
#     user = models.ForeignKey(
#         "auth.User",
#         on_delete=models.CASCADE,
#         related_name="reviews",
#         verbose_name=_("User"),
#     )
#     content = models.CharField(
#         max_length=255,
#         verbose_name=_("Review"),
#         help_text=_("Write your feedback here"),
#     )
#     rating = models.IntegerField(
#         choices=RATING_CHOICES, default=3, verbose_name=_("Rating")
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True, verbose_name=_("Created At")
#     )
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

#     class Meta:
#         verbose_name = _("Review")
#         verbose_name_plural = _("Reviews")
#         constraints = [
#             UniqueConstraint(fields=["product", "user"], name="unique_product_review")
#         ]
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
# """
#  CX32
# 4
# 8 GB
# 80 GB
# 20 TB
# $ 0.0127
# $ 7.59 max.
# """

# class Category(models.Model):
#     name = models.CharField(max_length=50, unique=True, verbose_name=_("Name Category"))
#     parent = models.ForeignKey("self", limit_choices_to={"parent__isnull": True}, on_delete=models.PROTECT,
#         verbose_name=_("Parent Category"),
#         blank=True,
#         null=True,
#         related_name="children",)

    
#     description = models.TextField(max_length=1000, verbose_name=_("Description"))
#     image = models.ImageField(
#         upload_to="category_pictures/", verbose_name=_("Image"), blank=True, null=True
#     )

#     slug = models.SlugField(
#         blank=True, max_length=255, null=True, unique=True, verbose_name=_("Slug")
#     )

#     class Meta:
#         verbose_name = _("Category")
#         verbose_name_plural = _("Categories")

#     def __str__(self):
#         return self.name

    
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = generate_category_slug(self.name)

#         # نحتاج نعرف هل الصورة تم تعديلها
#         image_needs_processing = self.image and not self.image.name.endswith(".webp")

#         if image_needs_processing:
#             # حول الصورة لـ WEBP
#             img = Image.open(self.image)
#             img = img.convert("RGB")
#             img.thumbnail((800, 800))

#             buffer = BytesIO()
#             img.save(buffer, format="WEBP", optimize=True, quality=75)

#             # تغيير الامتداد
#             name_without_ext = os.path.splitext(self.image.name)[0]
#             final_name = f"{name_without_ext}.webp"

#             # حفظ الصورة الجديدة بدون استدعاء .save() مرة تانية
#             self.image.save(final_name, ContentFile(buffer.getvalue()), save=False)

#         # حفظ نهائي مرة واحدة فقط
#         super().save(*args, **kwargs)

# class ProductImage(models.Model):
#     product = models.ForeignKey(
#         "product.Product", on_delete=models.CASCADE, verbose_name=_("Product"), related_name="product_images"
#     )
#     image = models.ImageField(upload_to="product_images/", verbose_name=_("Image"))

#     def __str__(self):
#         return f"Image for {self.product.name}"
    
#     def save(self, *args, **kwargs):
#         old_instance = None
#         if self.pk:
#             old_instance = ProductImage.objects.filter(pk=self.pk).first()

#         if self.image:
#             ext = os.path.splitext(self.image.name)[1].lower()
#             if ext != ".webp":
#                 img = Image.open(self.image)
#                 img = img.convert("RGB")
#                 img.thumbnail((800, 800))

#                 buffer = BytesIO()
#                 img.save(buffer, format="WEBP", optimize=True, quality=75)

#                 name_without_ext = self.image.name.rsplit(".", 1)[0]
#                 final_name = f"{name_without_ext}.webp"

#                 self.image.save(final_name, ContentFile(buffer.getvalue()), save=False)

#         with transaction.atomic():
#             super().save(*args, **kwargs)

#             # حذف الصورة القديمة بعد الحفظ لو كانت مختلفة
#             if old_instance and old_instance.image and old_instance.image != self.image:
#                 try:
#                     if os.path.isfile(old_instance.image.path):
#                         os.remove(old_instance.image.path)
#                 except Exception:
#                     pass


# class Color(models.TextChoices):
#     RED = "#f00", _("Red")
#     BROWN = "#a52a2a", _("Brown")
#     CYAN = "#00ffff", _("Cyan")
#     GOLD = "#ffd700", _("Gold")
#     BEIGE = "#f5f5dc", _("Beige")
#     CORAL = "#ff7f50", _("Coral")
#     INDIGO = "#4b0082", _("Indigo")
#     NAVY = "#000080", _("Navy")
#     BLACK = "#000", _("Black")
#     BLUE = "#00f", _("Blue")
#     GREEN = "#0f0", _("Green")
#     YELLOW = "#ff0", _("Yellow")
#     PINK = "#ffc0cb", _("Pink")
#     WHITE = "#fff", _("White")
#     LAVENDER = "#e6e6fa", _("Lavender")
#     GRAY = "#808080", _("Gray")
#     LIME = "#00ff00", _("Lime")
#     MAGENTA = "#ff00ff", _("Magenta")
#     MAROON = "#800000", _("Maroon")
#     MINT = "#98ff98", _("Mint")
#     OLIVE = "#808000", _("Olive")
#     ORANGE = "#ffa500", _("Orange")
#     PURPLE = "#800080", _("Purple")
#     SALMON = "#fa8072", _("Salmon")
#     SILVER = "#c0c0c0", _("Silver")
#     TEAL = "#008080", _("Teal")
#     TURQUOISE = "#40e0d0", _("Turquoise")
#     VIOLET = "#ee82ee", _("Violet")

# def color_image_upload_path(instance, filename):
#     return f"products/colors/{instance.product.id}/{filename}"

# class ProductColor(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"), related_name='colors')
#     color = models.CharField(max_length=20, choices=Color.choices)
#     image = models.ImageField(upload_to=color_image_upload_path, blank=True, null=True)

#     def __str__(self):
#         return _("{product} - Color: {color}").format(
#             product=self.product.name,
#             color=self.get_color_display()
#         )
    
#     def save(self, *args, **kwargs):
#         old_instance = None
#         if self.pk:
#             old_instance = ProductColor.objects.filter(pk=self.pk).first()

#         if self.image:
#             ext = os.path.splitext(self.image.name)[1].lower()
#             if ext != ".webp":
#                 img = Image.open(self.image)
#                 img = img.convert("RGB")
#                 img.thumbnail((800, 800))

#                 buffer = BytesIO()
#                 img.save(buffer, format="WEBP", optimize=True, quality=75)

#                 name_without_ext = self.image.name.rsplit(".", 1)[0]
#                 final_name = f"{name_without_ext}.webp"

#                 self.image.save(final_name, ContentFile(buffer.getvalue()), save=False)

#         with transaction.atomic():
#             super().save(*args, **kwargs)

#             if old_instance and old_instance.image and old_instance.image != self.image:
#                 try:
#                     if os.path.isfile(old_instance.image.path):
#                         os.remove(old_instance.image.path)
#                 except Exception:
#                     pass

# class Tag(models.Model):
#     name = models.CharField(verbose_name=_("Name"), max_length=100, unique=True)

#     class Meta:
#         verbose_name = _("Tag")
#         verbose_name_plural = _("Tags")
#         indexes = [models.Index(fields=["name"])]
#         ordering = ["name"]

#     def __str__(self):
#         return self.name

# @receiver(post_save, sender=Review)
# @receiver(post_delete, sender=Review)
# def update_product_rating(sender, instance, **kwargs):

#     instance.product.update_rating()
