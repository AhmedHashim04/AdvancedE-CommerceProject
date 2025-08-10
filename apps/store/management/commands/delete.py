from django.core.management.base import BaseCommand

from checkout.models import Order, OrderItem
from store.models import Category, Product, Review, ProductImage, Tag

# from payment.models import Payment


class Command(BaseCommand):
    help = "Deletes all product-related data (products, images, reviews, tags, categories, brands, collections ..)."

    def handle(self, *args, **kwargs):

        print("🧹 Deleting Orders...")
        Order.objects.all().delete()
        OrderItem.objects.all().delete()

        print("🧹 Deleting ProductImages...")
        ProductImage.objects.all().delete()

        print("🧹 Deleting Reviews...")
        Review.objects.all().delete()

        print("🧹 Deleting Products...")
        Product.objects.all().delete()

        print("🧹 Deleting Tags...")
        Tag.objects.all().delete()

        print("🧹 Deleting Categories...")
        Category.objects.exclude(parent=None).delete()
        Category.objects.all().delete()

        print("✅ All product-related data has been deleted.")
