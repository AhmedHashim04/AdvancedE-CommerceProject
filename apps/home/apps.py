from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.home"
    verbose_name = _("Home")  # ← هنا اسم التطبيق اللي هيظهر في لوحة التحكم
