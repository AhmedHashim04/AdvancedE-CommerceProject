
# import csv
# from django.shortcuts import render, redirect
# from django.urls import path
# from django.contrib import messages
# import io
# from django.contrib import admin
# from django.http import HttpResponse
# from django.utils.translation import gettext_lazy as _
# from project.admin import custom_admin_site
# from django.core.cache import cache
# from datetime import datetime
# from .models import Category, Product, Review, ProductImage, ProductColor, Tag
# from django import forms

# from django import forms
# from django.http import HttpResponse
# from django.shortcuts import render, redirect
# from django.urls import path
# from django.contrib import admin, messages
# from django.utils.translation import gettext_lazy as _
# import csv, io
# from .models import Product, ProductImage, ProductColor, Category


# class CSVImportForm(forms.Form):
#     csv_file = forms.FileField(label="Upload CSV File")


# @admin.action(description=_("Export selected products to CSV"))
# def export_products_to_csv(modeladmin, request, queryset):
#     opts = modeladmin.model._meta
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
#     filename = f"products_full_{timestamp}.csv"

#     response = HttpResponse(content_type="text/csv; charset=utf-8")
#     response["Content-Disposition"] = f"attachment; filename={filename}.csv"

#     writer = csv.writer(response)

#     # الحقول الأساسية من الـ Product
#     base_fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
#     header = [field.name for field in base_fields]

#     # الحقول الإضافية للعلاقات
#     header += ["category_name", "tags", "product_images", "colors"]

#     writer.writerow(header)

#     for obj in queryset.select_related("category").prefetch_related("tags", "product_images", "colors"):
#         row = []

#         # البيانات الأساسية
#         for field in base_fields:
#             val = getattr(obj, field.name)
#             row.append(str(val) if val is not None else "")

#         # اسم الكاتيجوري
#         row.append(obj.category.name if obj.category else "")

#         # الـ Tags
#         tags_list = [t.name for t in obj.tags.all()]
#         row.append(" || ".join(tags_list))

#         # الصور
#         images_list = [img.image.name for img in obj.product_images.all()]  # نخزن path النسبي
#         row.append(" || ".join(images_list))

#         # الألوان
#         colors_list = [
#             f"{c.color}::{c.image.name if c.image else ''}"
#             for c in obj.colors.all()
#         ]
#         row.append(" || ".join(colors_list))

#         writer.writerow(row)

#     return response

# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1


# class ProductColorInline(admin.TabularInline):
#     model = ProductColor
#     extra = 1


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     inlines = [ProductImageInline, ProductColorInline]
#     list_display = ("name", "price", "category", "available", "created_at", "overall_rating", "in_random_list")
#     list_filter = ("created_at", "available", "category", "in_random_list")
#     search_fields = ("name", "description", "category__name")
#     ordering = ("-created_at",)
#     actions = [export_products_to_csv]
#     exclude = ("slug",)
#     list_select_related = ("category",)
#     change_list_template = "admin/product_change_list.html"

#     def get_urls(self):
#         urls = super().get_urls()
#         return [path("import-csv/", self.import_csv, name="import-products-csv")] + urls

#     def import_csv(self, request):

#         if request.method == "POST":
#             form = CSVImportForm(request.POST, request.FILES)
#             if form.is_valid():
#                 csv_file = form.cleaned_data["csv_file"]
#                 decoded_file = csv_file.read().decode("utf-8")
#                 io_string = io.StringIO(decoded_file)
#                 reader = csv.DictReader(io_string)

#                 imported = 0
#                 for row in reader:
#                     try:
#                         # جلب أو إنشاء الكاتيجوري
#                         category_name = row.get("category_name", "").strip()
#                         category = None
#                         if category_name:
#                             category, _ = Category.objects.get_or_create(name=category_name)

#                         # إنشاء المنتج
#                         product = Product.objects.create(
#                             name=row["name"].strip(),
#                             price=row["price"],
#                             description=row.get("description", "").strip(),
#                             available=row.get("available", "False").lower() in ("true", "1", "yes"),
#                             category=category,
#                             image=row.get("image", None),
#                             discount=row.get("discount", 0) or 0,
#                             overall_rating=row.get("overall_rating", 0) or 0,
#                             owner_id=row.get("owner") or 1,
#                             in_random_list=row.get("in_random_list", "False").lower() in ("true", "1", "yes"),
#                             slug=row.get("slug") or None,
#                             trending=row.get("trending", "False").lower() in ("true", "1", "yes"),
#                             updated_at=row.get("updated_at") or datetime.datetime.now(),
#                             created_at=row.get("created_at") or datetime.datetime.now()
#                         )

#                         # ربط الـ Tags
#                         tags_raw = row.get("tags", "")
#                         if tags_raw:
#                             for tag_name in tags_raw.split(" || "):
#                                 tag_name = tag_name.strip()
#                                 if tag_name:
#                                     tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
#                                     product.tags.add(tag_obj)

#                         # إضافة الصور
#                         images_raw = row.get("product_images", "")
#                         if images_raw:
#                             for img_path in images_raw.split(" || "):
#                                 img_path = img_path.strip()
#                                 if img_path:
#                                     ProductImage.objects.create(product=product, image=img_path)

#                         # إضافة الألوان
#                         colors_raw = row.get("colors", "")
#                         if colors_raw:
#                             for color_item in colors_raw.split(" || "):
#                                 if "::" in color_item:
#                                     color_name, img_path = color_item.split("::", 1)
#                                     ProductColor.objects.create(
#                                         product=product,
#                                         color=color_name.strip(),
#                                         image=img_path.strip() if img_path.strip() else None
#                                     )

#                         imported += 1

#                     except Exception as e:
#                         messages.error(request, f"Error importing row {row.get('name', '')}: {str(e)}")
#                         continue

#                 messages.success(request, f"{imported} products imported successfully.")
#                 return redirect("..")
#         else:
#             form = CSVImportForm()

#         return render(request, "admin/csv_form.html", {"form": form})



# @admin.action(description=_("Export selected categories to CSV"))
# def export_categories_to_csv(modeladmin, request, queryset):
#     opts = modeladmin.model._meta
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
#     filename = f"categories_{timestamp}"

#     response = HttpResponse(content_type="text/csv; charset=utf-8")
#     response["Content-Disposition"] = f"attachment; filename={filename}"

#     writer = csv.writer(response)

#     # حدد الحقول اللي هتتحفظ (ممكن تضيف أو تعدل هنا)
#     fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
#     header = [field.name for field in fields]
#     writer.writerow(header)

#     for obj in queryset:
#         row = []
#         for field in fields:
#             val = getattr(obj, field.name)
#             # لو الحقل ForeignKey، خده كنص
#             row.append(str(val) if val is not None else "")
#         writer.writerow(row)

#     return response


# class CSVImportForm(forms.Form):
#     csv_file = forms.FileField(label="اختر ملف CSV")

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ("name", "parent", "description",)
#     list_filter = ("parent",)
#     search_fields = ("name", "description")
#     prepopulated_fields = {"slug": ("name",)}
#     actions = [export_categories_to_csv]
#     change_list_template = "admin/categories_changelist.html"  # هنضيف تمبليت مخصص

#     def get_urls(self):
#         from django.urls import path
#         urls = super().get_urls()
#         custom_urls = [
#             path('import-csv/', self.admin_site.admin_view(self.import_csv), name="category_import_csv"),
#         ]
#         return custom_urls + urls
#     def import_csv(self, request):
#         if request.method == "POST":
#             form = CSVImportForm(request.POST, request.FILES)
#             if form.is_valid():
#                 csv_file = form.cleaned_data["csv_file"]
#                 decoded_file = csv_file.read().decode("utf-8")
#                 io_string = io.StringIO(decoded_file)
#                 reader = list(csv.DictReader(io_string))  # نحولها لقائمة علشان نعدي عليها مرتين

#                 created_count = 0
#                 category_map = {}

#                 # المرحلة الأولى: إنشاء الأقسام بدون ربط parent
#                 for row in reader:
#                     name = row.get("name")
#                     slug = row.get("slug")
#                     description = row.get("description", "")
#                     image = row.get("image", "")

#                     category, created = Category.objects.get_or_create(
#                         name=name,
#                         defaults={
#                             "slug": slug,
#                             "description": description,
#                             "parent": None,
#                             "image": image
#                         }
#                     )
#                     category_map[name] = category
#                     if created:
#                         created_count += 1

#                 # المرحلة الثانية: ربط الأقسام بالأقسام الأب
#                 for row in reader:
#                     name = row.get("name")
#                     parent_name = row.get("parent_name")
#                     if parent_name:
#                         category = category_map.get(name)
#                         parent = category_map.get(parent_name)
#                         if category and parent:
#                             if category.parent_id != parent.id:
#                                 category.parent = parent
#                                 category.save()

#                 messages.success(request, f"تم استيراد {created_count} قسم بنجاح.")
#                 return redirect("..")
#         else:
#             form = CSVImportForm()

#         return render(request, "admin/import_csv_form.html", {"form": form})

# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ("product", "user", "content", "rating", "created_at")
#     list_filter = ("product", "created_at", "rating")
#     search_fields = ("content", "user__username", "product__name")
#     ordering = ("-created_at",)
#     autocomplete_fields = ["product", "user"]

# custom_admin_site.register(Category, CategoryAdmin)
# custom_admin_site.register(Product, ProductAdmin)
# # custom_admin_site.register(Review,ReviewAdmin) 
# admin.site.register(Tag)
# custom_admin_site.register(Tag)
