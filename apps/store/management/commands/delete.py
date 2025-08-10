from django.core.management.base import BaseCommand

from store.models import Product, Brand, Category, Tag, ProductImage, ProductColor, ShippingClass

# from payment.models import Payment


class Command(BaseCommand):
    help = "Deletes all product-related data (Products, Brands, Categories, Tags, ProductImages, ProductColors, ShippingClasses, ...)."

    def handle(self, *args, **kwargs):

        Product.objects.all().delete()
        Brand.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductColor.objects.all().delete()
        ShippingClass.objects.all().delete()

        print("✅ All product-related data has been deleted.")
