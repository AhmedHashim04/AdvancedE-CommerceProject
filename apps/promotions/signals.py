from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Promotion

@receiver(post_save, sender=Promotion)
def update_products(sender, instance, **kwargs):
    if instance.discount_type == 'percentage':

        if instance.apply_to == 'products':
            for product in instance.products.all():
                product.price = product.compare_at_price * (1 - instance.value / 100)
                product.save()
        
        elif instance.apply_to == 'tags':
            for tag in instance.tags.all():
                for product in tag.products.all():
                    product.price = product.compare_at_price * (1 - instance.value / 100)
                    product.save()
        
        elif instance.apply_to == 'categories':
            for category in instance.categorie.all():
                for product in category.products.all():
                    product.price = product.compare_at_price * (1 - instance.value / 100)
                    product.save()
        
        elif instance.apply_to == 'brands':
            for brand in instance.brand.all():
                for product in brand.products.all():
                    product.price = product.compare_at_price * (1 - instance.value / 100)
                    product.save()

    elif instance.discount_type == 'fixed':
        
        if instance.apply_to == 'products':
            for product in instance.products.all():
                product.price = product.compare_at_price - instance.value
                product.save()
        
        elif instance.apply_to == 'tags':
            for tag in instance.tags.all():
                for product in tag.products.all():
                    product.price = product.compare_at_price - instance.value
                    product.save()

        elif instance.apply_to == 'categories':
            for category in instance.categorie.all():
                for product in category.products.all():
                    product.price = product.compare_at_price - instance.value
                    product.save()
        
        elif instance.apply_to == 'brands':
            for brand in instance.brand.all():
                for product in brand.products.all():
                    product.price = product.compare_at_price - instance.value
                    product.save()

    elif instance.discount_type == 'free_shipping':

        if instance.apply_to == 'products':
            for product in instance.products.all():
                product.free_shipping = True
                product.save()
        
        elif instance.apply_to == 'tags':
            for tag in instance.tags.all():
                for product in tag.products.all():
                    product.free_shipping = True
                    product.save()

        elif instance.apply_to == 'categories':
            for category in instance.categorie.all():
                for product in category.products.all():
                    product.free_shipping = True
                    product.save()
 
        elif instance.apply_to == 'brands':
            for brand in instance.brand.all():
                for product in brand.products.all():
                    product.free_shipping = True
                    product.save()

    # elif instance.discount_type == 'bogo': #دي فال order
    # elif instance.discount_type == 'bxgy': #دي فال order
    
