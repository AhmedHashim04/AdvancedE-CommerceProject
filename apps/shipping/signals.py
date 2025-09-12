# في ملف signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem, Shipment, ShipmentItem, ShippingPlan

@receiver(post_save, sender=Order)
def create_shipments(sender, instance, created, **kwargs):
    if created:
        # تجميع عناصر الطلب حسب البائع وخطة الشحن
        seller_shipping_groups = {}
        
        for item in instance.items.all():
            product = item.product
            seller = product.seller
            shipping_plan = product.get_shipping_plan()
            
            # إذا لم توجد خطة شحن، نستخدم الخطة الافتراضية للبائع
            if not shipping_plan and seller.default_shipping_company:
                shipping_plan = seller.default_shipping_company.plans.filter(
                    governorate=instance.governorate
                ).first()
            
            if shipping_plan:
                key = (seller.id, shipping_plan.id)
                if key not in seller_shipping_groups:
                    seller_shipping_groups[key] = {
                        'seller': seller,
                        'shipping_plan': shipping_plan,
                        'items': []
                    }
                seller_shipping_groups[key]['items'].append(item)
        
        # إنشاء شحنة لكل مجموعة
        for key, group in seller_shipping_groups.items():
            shipment = Shipment.objects.create(
                order=instance,
                seller=group['seller'],
                shipping_plan=group['shipping_plan'],
                shipping_cost=calculate_shipping_cost(group['shipping_plan'], group['items'])
            )
            
            for item in group['items']:
                ShipmentItem.objects.create(
                    shipment=shipment,
                    order_item=item
                )

def calculate_shipping_cost(shipping_plan, items):
    total_weight = sum(item.product.weight * item.quantity for item in items)
    
    tier = shipping_plan.weight_tiers.filter(
        min_weight__lte=total_weight,
        max_weight__gte=total_weight
    ).first()
    
    if not tier:
        tier = shipping_plan.weight_tiers.order_by('-min_weight').first()
    
    return tier.price if tier else shipping_plan.base_price