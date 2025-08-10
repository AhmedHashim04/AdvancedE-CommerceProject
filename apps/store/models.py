from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

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


class ShippingClass(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

# -------------------------------------
# Main Product Model
# -------------------------------------

class Product(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default="EGP")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Stock
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    is_in_stock = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)

    # Media
    main_image = models.ImageField(upload_to="products/main_images/", blank=True, null=True)
    gallery = models.ManyToManyField(ProductImage, blank=True)
    video_url = models.URLField(blank=True, null=True)
    view_360_url = models.URLField(blank=True, null=True)

    # Shipping
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    depth = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    shipping_class = models.ForeignKey(ShippingClass, on_delete=models.SET_NULL, null=True, blank=True)

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    # Variants & Attributes
    has_variants = models.BooleanField(default=False)
    attributes = models.JSONField(blank=True, null=True)
    color_options = models.ManyToManyField(ProductColor, blank=True)

    # Admin & Stats
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.is_in_stock = self.stock_quantity > 0
        super().save(*args, **kwargs)

    def get_discounted_price(self):
        """حساب السعر بعد الخصم"""
        if self.discount_percentage:
            return self.price - (self.price * self.discount_percentage / 100)
        return self.price

    def get_seo_title(self):
        """إرجاع عنوان مناسب للـ SEO"""
        return self.meta_title if self.meta_title else self.name

    def is_low_stock(self):
        """تحقق إذا المخزون قليل"""
        return self.stock_quantity <= self.low_stock_threshold

    def __str__(self):
        return self.name
