import json

import pytest
from django.core.cache import cache
from django.urls import reverse


@pytest.mark.django_db
class TestIndexView:

    def test_post_add_to_basket_success(self, client, create_product):
        """测试POST请求,成功将商品添加到购物车"""
        url = reverse("store:index")
        payload = {"product_id": create_product.id, "product_qty": 2}
        response = client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == 200
        assert response.json() == {"qty": 2}
        session = client.session
        assert "basket" in session
        assert str(create_product.id) in session["basket"]

    def test_get_default_index_cache(self, client, create_product):
        """测试GET请求,使用缓存加载数据"""
        mock_context = {
            "products": [create_product],
            "active_category": None,
            "page_range": [1],
            "is_discount": None,
        }
        cache.set("store_index_default_list", mock_context, timeout=3600)
        url = reverse("store:index")
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["products"] == [create_product]

    def test_get_index_cache_miss_and_set(self, client, create_product, create_user):
        """测试GET请求,不使用缓存加载数据,并设置缓存"""
        client.force_login(create_user)
        cache.clear()
        url = reverse("store:index")
        response = client.get(url)

        assert response.status_code == 200
        cache_data = cache.get("store_index_default_list")
        assert cache_data is not None
        assert len(cache_data["products"]) == 1
        assert create_product.id in response.context["user_wishlist_ids"]

    def test_get_active_category(self, client, create_category, create_product):
        """测试GET请求,测试分类"""
        url = reverse("store:category_product", args=[create_category.slug])
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context["products"]) == 1

    def test_get_is_discount(self, client, create_product):
        """测试GET请求,测试打折专区"""
        url = reverse("store:index") + "?discount=true"
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context["products"]) == 1


@pytest.mark.django_db
def test_get_product_detail_success(
    client, create_category, create_product, create_user
):
    """测试商品详情页成功加载商品"""
    client.force_login(create_user)
    url = reverse(
        "store:product_detail", args=[create_category.slug, create_product.slug]
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["is_in_wishlist"] is True


@pytest.mark.django_db
def test_get_product_detail_out_stock_404(client, create_category, create_product):
    """测试商品库存不足,跳转到404"""
    create_product.stock = 0
    create_product.save()
    url = reverse(
        "store:product_detail", args=[create_category.slug, create_product.slug]
    )
    response = client.get(url)
    assert response.status_code == 404
