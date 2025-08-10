from django.core.management.base import BaseCommand

from store.models import Tag

TAGS = [
    "إلكترونيات", "ملابس", "أحذية", "ساعات", "مجوهرات", "موبايلات", "أجهزة منزلية", "أثاث",
    "عناية بالبشرة", "عناية بالشعر", "مكياج", "ألعاب أطفال", "كتب", "مستلزمات مدرسية",
    "هدايا رجالي", "هدايا نسائية", "هدايا أطفال", "هدايا عيد ميلاد", "هدايا رومانسية",
    "هدايا خطوبة", "هدايا زفاف", "هدايا عيد الحب", "هدايا تخرج", "هدايا نجاح",
    "هدايا رمضان", "هدايا العيد", "هدايا رأس السنة", "هدايا فخمة", "هدايا بسيطة",
    "صناديق هدايا", "هدايا يدوية", "هدايا مخصصة", "تغليف هدايا", "بطاقات معايدة",
    "شوكولاتة", "دباديب", "ألعاب هدايا", "كروت تهنئة", "بوكيهات ورد", "إكسسوارات هدايا",
    "مج حراري", "ساعات هدايا", "مفاتيح مميزة", "لوحات فنية", "دفاتر هدايا", "هدايا أنيقة",
    "ديكورات رومانسية", "عطور هدايا", "علب خشب", "هدايا مكتبية", "ميداليات", "شموع معطرة",
    "جديد", "وصل حديثًا", "الأكثر مبيعًا", "عرض خاص", "خصم", "وفر الآن", "موسم التخفيضات",
    "عروض العيد", "صفقات اليوم", "لفترة محدودة", "أفضل سعر", "الفرصة الأخيرة", "اشترِ 1 واحصل على 1",
]

class Command(BaseCommand):
    help = "Seed initial tags into the database"

    def handle(self, *args, **kwargs):
        created_count = 0
        for tag_name in TAGS:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Added tag: {tag_name}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"• Already exists: {tag_name}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Total new tags added: {created_count}"))
