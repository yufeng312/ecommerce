from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.http import Http404

def index(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'store/home.html', context)

def all_products(request):
    return {
        'products': Product.objects.all()
    }

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