from django.db import models

from account.models import User
from store.models import Product


class Order(models.Model):
    class StatusChoices(models.IntegerChoices):
        UNKNOW = 0, '未知'
        PENDING_PAY = 10, '待付款'
        PENDING_SHIPPED = 20, '待发货'
        SHIPPED = 30, '已发货'
        RECEIVED = 40, '已收货'
        CANCELLED = 50, '已取消'

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    order_sn = models.CharField(max_length=30, unique=True, verbose_name='订单编号')
    status = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING_PAY, verbose_name='订单状态')
    address = models.CharField(max_length=255, blank=False, verbose_name='收货地址')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name='商品总价')
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='运费')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='优惠金额')
    payment_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name='实际支付金额')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='订单创建时间')
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name='支付时间')
    cancel_time = models.DateTimeField(blank=True, null=True, verbose_name='取消时间')
    note = models.TextField(blank=True, verbose_name='订单备注')

    class Meta:
        db_table = 'order'
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def __str__(self):
        return self.order_sn
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product_name = models.CharField(max_length=255, verbose_name='商品名称')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='下单时单价')
    quantity = models.IntegerField(verbose_name='购买数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='小计金额')

    class Meta:
        db_table = 'orderitem'
        verbose_name = '订单清单'
        verbose_name_plural = '订单清单'

    def __str__(self):
        return self.product_name