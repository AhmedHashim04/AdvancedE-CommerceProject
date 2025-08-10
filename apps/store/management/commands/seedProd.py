import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from slugify import slugify
from faker import Faker
from store.models import Product, Category, Tag, ProductImage, ProductColor, Color
from django.db import transaction

fake = Faker("ar_EG")

# IMAGE_DIR = "/home/ahmed/Desktop/venv/src/media/base-images"
IMAGE_DIR = "/home/ahmed/venv/src/media/base-images"
TARGET_COUNT = 5000  # عدد المنتجات المطلوب إنشاؤها

class Command(BaseCommand):
    help = "⚙️ Seed massive number of products using repeated images."

    def handle(self, *args, **kwargs):
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())

        if not categories or not tags:
            self.stdout.write(self.style.ERROR("❌ Categories or Tags missing."))
            return

        image_files = sorted([
            os.path.join(IMAGE_DIR, f)
            for f in os.listdir(IMAGE_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ])

        if len(image_files) == 0:
            self.stdout.write(self.style.ERROR("❌ No images found in the directory."))
            return

        original_image_count = len(image_files)
        self.stdout.write(f"📸 Found {original_image_count} source images. Generating {TARGET_COUNT} products...")

        created_products = []
        product_images = []
        product_colors = []

        image_index = 0

        with transaction.atomic():
            for i in range(TARGET_COUNT):
                category = random.choice(categories)
                name = fake.unique.sentence(nb_words=3).replace(".", "")
                slug = slugify(name) + f"-{random.randint(1000, 9999)}"
                price = round(random.uniform(10, 1000), 2)
                discount = random.choice([0, 5, 10, 15, 20])

                product = Product(
                    name=name,
                    category=category,
                    description=fake.text(max_nb_chars=500),
                    price=Decimal(price),
                    discount=Decimal(discount),
                    available=True,
                    trending=random.choice([True, False]),
                    in_random_list=random.choice([True, False]),
                    slug=slug
                )

                created_products.append((product, image_index))
                image_index += 6

                if (i + 1) % 100 == 0:
                    self.stdout.write(f"✅ Prepared {i + 1} products...")

            # إنشاء المنتجات دفعة واحدة
            Product.objects.bulk_create([p for p, _ in created_products], batch_size=500)

            # إعادة تحميل المنتجات من قاعدة البيانات
            products = Product.objects.order_by("-id")[:TARGET_COUNT][::-1]

            # مؤشرات التقدم
            image_counter = 0
            color_counter = 0

            for (product, index), db_product in zip(created_products, products):
                # الصورة الرئيسية
                main_img_path = image_files[index % original_image_count]
                with open(main_img_path, 'rb') as f:
                    filename = os.path.basename(main_img_path)
                    db_product.image.save(filename, ContentFile(f.read()), save=True)

                # صور إضافية (ProductImage)
                for j in range(1, 4):
                    img_path = image_files[(index + j) % original_image_count]
                    with open(img_path, 'rb') as f:
                        product_images.append(ProductImage(
                            product=db_product,
                            image=ContentFile(f.read(), name=os.path.basename(img_path))
                        ))
                        image_counter += 1
                        if image_counter % 100 == 0:
                            self.stdout.write(f"🖼️ Created {image_counter} product images...")

                # صور ProductColor
                for j in range(4, 6):
                    img_path = image_files[(index + j) % original_image_count]
                    with open(img_path, 'rb') as f:
                        product_colors.append(ProductColor(
                            product=db_product,
                            color=random.choice(Color.values),
                            image=ContentFile(f.read(), name=os.path.basename(img_path))
                        ))
                        color_counter += 1
                        if color_counter % 100 == 0:
                            self.stdout.write(f"🎨 Created {color_counter} product color images...")

                # التاجات
                db_product.tags.add(*random.sample(tags, random.randint(1, 3)))

            # حفظ الصور دفعة واحدة
            ProductImage.objects.bulk_create(product_images, batch_size=500)
            ProductColor.objects.bulk_create(product_colors, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f"🎉 Successfully created {TARGET_COUNT} products using repeated images."))
