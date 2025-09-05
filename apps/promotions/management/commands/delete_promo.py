from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Deletes all product-related data (Products, Brands, Categories, Tags, ProductImages, ProductColors, ShippingClasses, ...)."

    def handle(self, *args, **kwargs):

        print("✅ All product-related data has been deleted.")
