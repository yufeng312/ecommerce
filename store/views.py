import json

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import (Http404, JsonResponse)

from .models import Product, Category
from basket.basket import Basket

def index(request, category_slug=None):
    """
    商城首页
    """
    basket = Basket(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        product = get_object_or_404(Product, pk=product_id)
        product_qty= int(data.get('product_qty', 1))
        basket.add(product=product, qty=product_qty)
        basket.save()
        return JsonResponse({'qty': len(basket)})
    else:
        page_num = request.GET.get('page', 1)
        categories = Category.objects.all()
        products = Product.products.all()
        active_category = None
        if category_slug:
            active_category = get_object_or_404(Category, slug=category_slug)
            products = Product.products.filter(category=active_category)
        paginator = Paginator(products, 16)
        products = paginator.get_page(page_num)
        page_range = paginator.get_elided_page_range(products.number, on_each_side=3, on_ends=2)
        context = {
            'categories': categories,
            'products': products,
            'active_category': active_category,
            'page_range': page_range
        }
        return render(request, 'store/index.html', context)

def product_detail(request, category, product):
    """
    商品详情页
    """
    product = get_object_or_404(Product, slug=product)
    if product.stock > 0:
        category = get_object_or_404(Category, slug=category)
        context = {
            'product': product,
            'category': category
        }
        return render(request, 'store/detail.html', context)
    else:
        return render(request, 'store/detail_404.html', status=404)