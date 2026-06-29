import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Basket
from store.models import Product

def basket_summary(request):
    """
    购物车页面
    """
    return render(request, 'store/basket/basket.html')

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
    
def basket_debug(request):
    """
    测试session数据是否正确
    """
    return JsonResponse(request.session.get('skey', {}))