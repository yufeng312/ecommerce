import random
import datetime
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.shortcuts import (render, HttpResponse, redirect, get_object_or_404)
from django.contrib.auth.decorators import login_required

from basket.basket import Basket
from store.models import Product
from .models import (Order, OrderItem)


@login_required
def order_confirm(request):
    """
    进入订单确认页
    """
    basket = Basket(request)
    address = '山东省青岛市李沧区XXXX'
    user = request.user
    context = {
        'basket': basket,
        'address': address,
        'user': user
    }
    return render(request, 'account/order/order_confirm.html', context=context)

@login_required
def order_create(request):
    """
    用户在确认页点击去付款,通过post表单请求该接口
    """
    if request.method != 'POST':
        return redirect('basket:basket_summary')
    
    basket = Basket(request)
    if len(basket) == 0:
        messages.error(request, '您的购物车空空如也,无法下单')
        return redirect('basket:basket_summary')
    
    address = request.POST.get('order-address', '')
    note = request.POST.get('order-note', '')

    now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    user_id_str = str(request.user.id).zfill(5)
    random_str = str(random.randint(1000, 9999))
    order_sn = f'{now_time}{user_id_str}{random_str}'

    try:
        with transaction.atomic():
            order = Order.objects.create(
                    user=request.user,
                    order_sn=order_sn,
                    status=10,  # 待付款
                    address=str(address),
                    total_price=basket.total_price,
                    freight=basket.freight,
                    discount_price=basket.discount_price,
                    payment_price=basket.total_payable,
                    note = note
            )
            for item in basket:
                product = item['product']
                qty = int(item['qty'])
                # 加锁,防止超库存
                product_db = Product.objects.select_for_update().get(pk=product.id)
                if qty > product_db.stock:
                    raise ValueError(f'商品[{product.name}]库存不足,目前仅剩[{product.stock}]件')
                product.stock -= qty
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    image = product.image,
                    price=product.discount_price,
                    quantity=qty,
                    total_price=item['total_price']
                )
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('basket:basket_summary')
    except Exception as e:
        messages.error(request, '系统繁忙,订单创建失败,请稍后重试')
        print(e)
        return redirect('basket:basket_summary')
    
    basket.clear()
    return render(request, 'account/order/order_payment.html', {'order_sn': order_sn})
    
@login_required
def order_payment(request, order_sn):
    """
    付款成功时,修改订单状态
    """
    order = get_object_or_404(Order, order_sn=order_sn, user=request.user)

    # 在订单状态是10(未付款)时,修改成20(已付款)
    if order.status == 10:
        order.status = 20
        order.payment_time = timezone.now()  # 记录付款时间
        order.save()
        messages.success(request, f'订单{order_sn}支付成功!')
    else:
        messages.warning(request, '该订单不需要重复支付')

    return redirect('order:order_detail', order_sn=order_sn)

@login_required
def order_cancel(request, order_sn):
    """
    点击取消付款时,修改订单状态
    """
    order = get_object_or_404(Order, order_sn=order_sn, user=request.user)

    # 在订单状态是10(未付款)时,修改成50(已取消)
    if order.status == 10:
        order.status = 50
        order.cancel_time = timezone.now()  # 记录取消时间
        order.save()

        # 找到对应商品,恢复库存
        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            order_item.product.stock += order_item.quantity
            order_item.product.save()
        
        messages.success(request, '订单已成功取消')
    else:
        messages.warning(request, '该订单无法取消或已处理')
    return render(request, 'account/order/order_cancel.html', {'order_sn': order_sn})

@login_required
def order_detail(request, order_sn):
    """
    订单详情页面
    """
    order = get_object_or_404(Order, order_sn=order_sn, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'account/order/order_detail.html', context=context)
