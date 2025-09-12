from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from faker import Faker
import requests
import random
from apps.promotions.models import Promotion 
from apps.store.models import Product, Brand, Category, Tag, ProductImage, ProductColor
from apps.sellers.models import Seller as User  # Assuming Seller is a subclass of User
fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with sample data for E-Commerce models"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Starting database seeding..."))

        # Create Brands
        brands = []
        for _ in range(5):
            brand = Brand.objects.create(
                name=fake.company(),
                description=fake.text(),
            )
            brands.append(brand)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(brands)} brands"))

        # Create Categories
        categories = []
        for _ in range(5):
            cat = Category.objects.create(
                name=fake.word().capitalize(),
                description=fake.text()
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(categories)} categories"))

        # Create Tags
        tags = []
        for _ in range(10):
            tag = Tag.objects.create(name=fake.word().capitalize())
            tags.append(tag)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(tags)} tags"))

        # Create Colors
        colors = []
        color_names = ["Red", "Blue", "Green", "Black", "White", "Yellow"]
        for name in color_names:
            color = ProductColor.objects.create(
                name=name,
                hex_code=fake.hex_color()
            )
            colors.append(color)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(colors)} colors"))

        # Create Product Images
        # images = []
        # for _ in range(15):
        #     img_url = f"https://picsum.photos/500/500?random={random.randint(1, 1000)}"
        #     img = ProductImage.objects.create()
        #     img_data = requests.get(img_url).content
        #     img.image.save(f"product_{random.randint(1,1000)}.jpg", ContentFile(img_data), save=True)
        #     img.alt_text = fake.sentence()
        #     img.save()
        #     images.append(img)
        # self.stdout.write(self.style.SUCCESS(f"✅ Created {len(images)} product images"))

        # Create Products
        for _ in range(20):
            product = Product.objects.create(
                seller=User.objects.first(),  # تأكد من وجود مستخدم في النظام
                name=fake.sentence(nb_words=3),
                description=fake.text(),
                short_description=fake.sentence(),
                # sku=f"SKU-{random.randint(1000,9999)}",
                # barcode=str(random.randint(100000000000, 999999999999)),
                brand=random.choice(brands),
                category=random.choice(categories),
                promotion=random.choice(Promotion.objects.all()) if Promotion.objects.exists() else None,
                base_price=round(random.uniform(100, 1000), 2),
                cost_price=round(random.uniform(50, 500), 2),
                stock_quantity=random.randint(0, 50),
                low_stock_threshold=5,
                is_active=True,
                is_featured=random.choice([True, False]),
                weight=random.uniform(0.5, 5.0),
                width=random.uniform(10, 50),
                height=random.uniform(10, 50),
                depth=random.uniform(10, 50),

            )

            # # Add random tags, colors, and images
            # product.tags.add(*random.sample(tags, k=random.randint(1, 3)))
            # product.color_options.add(*random.sample(colors, k=random.randint(1, 2)))

            # # Main image
            # main_img_url = f"https://picsum.photos/500/500?random={random.randint(1, 1000)}"
            # main_img_data = requests.get(main_img_url).content
            # product.main_image.save(f"main_{product.id}.jpg", ContentFile(main_img_data), save=True)

            # # Gallery
            # product.gallery.add(*random.sample(images, k=random.randint(1, 3)))

        self.stdout.write(self.style.SUCCESS("🎯 Database seeding completed successfully!"))
