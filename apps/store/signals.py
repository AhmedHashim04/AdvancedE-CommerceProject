from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product

@receiver(post_save, sender=Product)
def update_stock_status(sender, instance, **kwargs):
    """تحديث حالة توفر المنتج تلقائيًا"""
    if instance.stock_quantity > 0:
        instance.is_in_stock = True
    else:
        instance.is_in_stock = False
    Product.objects.filter(pk=instance.pk).update(is_in_stock=instance.is_in_stock)

@receiver(post_delete, sender=Product)
def delete_related_images(sender, instance, **kwargs):
    """حذف صور المنتج عند حذفه"""
    if instance.main_image:
        instance.main_image.delete(save=False)
    for img in instance.gallery.all():
        img.image.delete(save=False)
