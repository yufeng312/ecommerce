from django.urls import path

from . import views

app_name = 'order'

urlpatterns = [
    path('confirm/', views.order_confirm, name='order_confirm'),  # 订单确认页
    path('create/', views.order_create, name='order_create'),  # 创建订单
    path('payment/<str:order_sn>', views.order_payment, name='order_payment'),  # 付款成功
    path('cancel/<str:order_sn>', views.order_cancel, name='order_cancel'),  # 取消按钮/付款失败
    path('order-detail/<str:order_sn>', views.order_detail, name='order_detail'),  # 订单详情页
]
