from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Product, Category

def index(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.all()
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=active_category)
    context = {
        'categories': categories,
        'products': products,
        'active_category': active_category,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, category, product):
    product = get_object_or_404(Product, slug=product)
    if product.stock > 0:
        category = get_object_or_404(Category, slug=category)
        context = {
            'product': product,
            'category': category
        }
        return render(request, 'store/products/detail.html', context)
    else:
        raise Http404('该商品目前没货')