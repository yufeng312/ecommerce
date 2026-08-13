from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    path("confirm/", views.order_confirm, name="order_confirm"),  # 订单确认页
    path("create/", views.order_create, name="order_create"),  # 创建订单
    path(
        "cancel/<str:order_sn>", views.order_cancel, name="order_cancel"
    ),  # 取消按钮/付款失败
    path(
        "order-detail/<str:order_sn>", views.order_detail, name="order_detail"
    ),  # 订单详情页
    path(
        "alipay/pay/<str:order_sn>", views.alipay_pay_view, name="alipay_pay"
    ),  # 付款页面
    path(
        "alipay/return/", views.alipay_return, name="alipay_return"
    ),  # 支付成功显示页面
    path(
        "alipay/notify/", views.alipay_notify, name="alipay_notify"
    ),  # 异步数据回调地址
]
