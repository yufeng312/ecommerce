from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Product

@receiver([post_delete, post_save], sender=Product)
def clear_index_products_cache(sender, instance, **kwargs):
    """当商品新增,修改或删除时,自动删除首页缓存"""
    cache_key = 'store_index_default_list'
    cache.delete(cache_key)