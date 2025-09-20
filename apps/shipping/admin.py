from django.contrib import admin
from .models import Governorate, City, Address, ShippingCompany, ShippingPlan, Shipment, WeightPricing

admin.site.register(Governorate)
admin.site.register(City)
admin.site.register(Address)
admin.site.register(ShippingCompany)
admin.site.register(ShippingPlan)
admin.site.register(Shipment)
admin.site.register(WeightPricing)