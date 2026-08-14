from celery import shared_task
from django.db import transaction
from django.db.models import F

from store.models import Product

from .models import Order


@shared_task
def cancel_unpaid_order_task(order_sn):
    """30分钟未支付,自动取消订单并归还库存"""
    try:
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .filter(order_sn=order_sn, status=10)
                .first()
            )
            if not order:
                return f"订单 {order_sn} 状态非待付款,跳过自动取消"
            order.status = 50
            order.save(update_fields=["status"])
            for item in order.order_items.all():
                Product.objects.filter(id=item.product_id).update(
                    stock=F("stock") + item.quantity
                )
            return f"订单 {order_sn} 超过30分钟未支付,系统自动取消并归还库存"
    except Exception as e:
        return f"取消订单 {order_sn} 异常: {str(e)}"
