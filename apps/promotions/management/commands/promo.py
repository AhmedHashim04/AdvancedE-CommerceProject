from django.core.management.base import BaseCommand
from faker import Faker
from apps.promotions.models import Promotion, BQGPromotion
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.store.models import Product  # تأكد أن هذا import صحيح

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with sample data for E-Commerce models"
    def handle(self, *args, **kwargs):
        products = Product.objects.all()

        # Create BQGPromotion-only promotions (no percentage/fixed discounts)
        for _ in range(5):
            gift_product = fake.random_element(elements=products)
            bqg = BQGPromotion.objects.create(
                quantity_to_buy=fake.random_int(min=1, max=5),
                gift=gift_product,
                gift_quantity=fake.random_int(min=1, max=3),
                percentage_amount=None,
                fixed_amount=None,
            )
            Promotion.objects.create(
                value=None,
                bqg=bqg,
                is_active=True,
                start_date=timezone.now() - timedelta(days=1),
                end_date=timezone.now() + timedelta(days=30),
                usage_limit=fake.random_int(min=10, max=100),
                usage_count=fake.random_int(min=0, max=10),
            )

        # Create percentage-only promotions (no fixed, no BQG)
        for _ in range(3):
            Promotion.objects.create(
                value=None,
                bqg=None,
                is_active=True,
                start_date=timezone.now() - timedelta(days=1),
                end_date=timezone.now() + timedelta(days=30),
                usage_limit=fake.random_int(min=10, max=100),
                usage_count=fake.random_int(min=0, max=10),
            )

        # Create fixed-only promotions (no percentage, no BQG)
        for _ in range(2):
            Promotion.objects.create(
                value=None,
                bqg=None,
                is_active=True,
                start_date=timezone.now() - timedelta(days=1),
                end_date=timezone.now() + timedelta(days=30),
                usage_limit=fake.random_int(min=10, max=100),
                usage_count=fake.random_int(min=0, max=10),
            )

        self.stdout.write(self.style.SUCCESS("Seeded promotions and BQGPromotions successfully!"))