from django.contrib import admin
from .models import Promotion ,FlashSale ,PromotionUsage ,LoyaltyProgram ,LoyaltyPoints

admin.site.register(Promotion)
admin.site.register(FlashSale)
admin.site.register(PromotionUsage)
admin.site.register(LoyaltyProgram)
admin.site.register(LoyaltyPoints)

