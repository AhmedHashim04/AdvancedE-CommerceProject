import json
import os
import django

# تأكد من تغيير 'myproject.settings' لاسم settings بتاع مشروعك
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from apps.shipping.models import Governorate, City


with open('placements/governorates.json', encoding='utf-8') as f:
    governorates = json.load(f)

with open('placements/cities.json', encoding='utf-8') as f:
    cities = json.load(f)

for gov in governorates:
    gov_id = gov.get('id')
    if not gov_id:
        continue  # تجاهل أي عنصر ناقص
    Governorate.objects.update_or_create(
        code=gov_id,
        defaults={
            'name_ar': gov.get('governorate_name_ar', ''),
            'name_en': gov.get('governorate_name_en', '')
        }
    )


for city in cities:
    gov_id = city.get('governorate_id')
    if not gov_id:
        print(f"تجاهل عنصر ناقص governorate_id: {city}")
        continue
    governorate = Governorate.objects.get(code=gov_id)
    City.objects.update_or_create(
        code=city.get('id', ''),
        governorate=governorate,
        defaults={
            'name_ar': city.get('city_name_ar', ''),
            'name_en': city.get('city_name_en', '')
        }
    )
