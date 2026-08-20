import json

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from basket.basket import Basket

from .models import Category, Product


def index(request, category_slug=None):
    """
    商城首页
    """
    basket = Basket(request)
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = str(data.get("product_id"))
        product = get_object_or_404(Product, pk=product_id)
        product_qty = int(data.get("product_qty", 1))
        basket.add(product=product, qty=product_qty)
        basket.save()
        return JsonResponse({"qty": len(basket)})
    else:
        page_num = request.GET.get("page", 1)
        is_discount = request.GET.get("discount")
        # 判断是否是纯首页数据
        is_default_index = (
            category_slug is None and is_discount != "true" and str(page_num) == "1"
        )
        user_wishlist_ids = set()
        if request.user.is_authenticated:
            # flat=True让查询出的元组列表变成直接的id列表
            user_wishlist_ids = set(
                request.user.user_wishlist.values_list("id", flat=True)
            )
        if is_default_index:
            cache_key = "store_index_default_list"
            cached_context = cache.get(cache_key)
            if cached_context:
                cached_context["user_wishlist_ids"] = user_wishlist_ids
                return render(request, "store/index.html", cached_context)
        products = (
            Product.products.select_related("category")
            .prefetch_related("product_image")
            .all()
        )
        active_category = None
        if category_slug:
            active_category = get_object_or_404(Category, slug=category_slug)
            category_family = active_category.get_descendants(include_self=True)
            products = products.filter(category__in=category_family)
        if is_discount == "true":
            products = products.filter(is_discount=True)
        paginator = Paginator(products, 16)
        products = paginator.get_page(page_num)
        page_range = list(
            paginator.get_elided_page_range(products.number, on_each_side=3, on_ends=2)
        )
        context = {
            "products": products,
            "active_category": active_category,
            "page_range": page_range,
            "is_discount": is_discount,
        }
        # 将缓存存入redis
        if is_default_index:
            cache.set("store_index_default_list", context, timeout=3600)
        context["user_wishlist_ids"] = user_wishlist_ids
        return render(request, "store/index.html", context)


def product_detail(request, category, product):
    """
    商品详情页
    """
    product = get_object_or_404(
        Product.objects.prefetch_related("product_image"), slug=product
    )
    if product.stock > 0:
        category = get_object_or_404(Category, slug=category)
        is_in_wishlist = product.user_wishlist.filter(id=request.user.id).exists()
        context = {
            "product": product,
            "category": category,
            "is_in_wishlist": is_in_wishlist,
        }
        return render(request, "store/detail.html", context)
    else:
        return render(request, "store/detail_404.html", status=404)
