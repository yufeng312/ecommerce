from django.contrib import admin

from .models import (Order, OrderItem)


admin.site.register(OrderItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_sn', 'status', 'payment_price', 'created_time']

    # 设置只读字段,显示订单创建时间
    readonly_fields = ['created_time', 'payment_time', 'cancel_time', 'note']