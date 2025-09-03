from django.db import models
from django.db.models import Q
from django.utils.text import slugify
from apps.sellers.models import Seller, ShippingSystem
from apps.promotions.models import Promotion#, FlashSale
from apps.coupons.models import Coupon

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# -------------------------------------
# Related Models
# -------------------------------------

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="brands/logos/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductColor(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, help_text="مثال: #FFFFFF")

    def __str__(self):
        return f"{self.name} ({self.hex_code})"


class ProductImage(models.Model):
    image = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.alt_text or self.image.url


# -------------------------------------
# Main Product Model
# -------------------------------------
class Currency(models.TextChoices):
    EGP = "EGP", _("Egyptian Pound")
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")
    GBP = "GBP", _("British Pound")
    JPY = "JPY", _("Japanese Yen")
    AUD = "AUD", _("Australian Dollar")


class SEOFieldsMixin(models.Model):
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

class Product(SEOFieldsMixin, models.Model):

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)

    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, related_name="products")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name="products", db_index=True)
    tags = models.ManyToManyField('Tag', blank=True)

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="products",editable=False)
    shipping_system = models.OneToOneField(ShippingSystem, on_delete=models.SET_NULL, null=True, related_name="product")

    price = models.DecimalField(default=0, max_digits=10, decimal_places=2,editable=False)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EGP)
    tax_rate = models.DecimalField(default=0, max_digits=5, decimal_places=2, blank=True, null=True)

    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    allow_backorder = models.BooleanField(default=False)

    main_image = models.ImageField(upload_to="products/main_images/", blank=True, null=True)
    gallery = models.ForeignKey(ProductImage, on_delete=models.CASCADE, blank=True, null=True, related_name="product_gallery")
    video_url = models.URLField(blank=True, null=True)
    view_360_url = models.URLField(blank=True, null=True)

    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    depth = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)


    has_variants = models.BooleanField(default=False) #--> different versions of the product (S, M, L, XL) , 
    attributes = models.JSONField(blank=True, null=True)
    color_options = models.ManyToManyField('ProductColor', blank=True)



    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    views_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)

    is_on_sale = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  
        self.apply_promotions()
        super().save(*args, **kwargs)

    def get_seo_title(self):
        return self.meta_title if self.meta_title else self.name

    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    def get_volume(self):
        if self.width and self.height and self.depth:
            return self.width * self.height * self.depth
        return None

    def __str__(self):
        return self.name

