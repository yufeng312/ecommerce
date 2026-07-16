import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .basket import Basket
from store.models import Product

def basket_summary(request):
    """
    购物车页面
    """
    basket = Basket(request)
    return render(request, 'store/basket/basket.html', {'basket': basket})

def basket_add(request):
    """
    获取购物车中的商品总数,返回给前端
    """
    basket = Basket(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product_qty = data.get('product_qty')
        product = get_object_or_404(Product, id=product_id)
        basket.add(product=product, qty=product_qty)
        productqty = basket.__len__()
        response = JsonResponse({'qty': int(productqty)})
        return response
    
def basket_update(request):
    """
    更新商品数量,修改存储在session中的商品数量
    """
    basket = Basket(request)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product_qty = data.get('product_qty')

            if product_qty < 1:
                return JsonResponse({'status': 'error', 'message': '数量非法'})
            product = get_object_or_404(Product, id=product_id)
            basket.update(product=product, qty=product_qty)
            return JsonResponse({'status': 'success', 'message': '更新成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
def basket_delete(request):
    """
    删除购物车商品,删除session中的对应数据
    """
    basket = Basket(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        basket.delete(product_id)
        category_count = basket.category_count
        return JsonResponse({'status': 'success', 'message': '数据成功删除', 'category_count': category_count})
        
def basket_debug(request):
    """
    测试session数据是否正确
    """
    return JsonResponse(request.session.get('skey', {}))