import json

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_basket_summary(create_basket):
    """测试购物车主页,以及session中是否存储数据"""
    url = reverse("basket:basket_summary")
    response = create_basket.get(url)
    assert response.status_code == 200
    assert "basket" in create_basket.session


@pytest.mark.django_db
def test_basket_add_success(client, create_product):
    """测试成功向购物车中添加数据"""
    product_id = create_product.id
    product_qty = 2
    url = reverse("basket:basket_add")
    payload = {"product_id": product_id, "product_qty": product_qty}
    response = client.post(url, json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    assert response.json() == {"qty": 2}
    assert str(product_id) in client.session.get("basket", {})


@pytest.mark.django_db
def test_basket_update_success(create_product, create_basket):
    """测试成功修改购物车数据"""
    product_id = create_product.id
    product_qty = 4
    url = reverse("basket:basket_update")
    payload = {"product_id": product_id, "product_qty": product_qty}
    response = create_basket.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "更新成功"}
    update_basket = create_basket.session.get("basket")
    assert update_basket[str(product_id)]["qty"] == 4


@pytest.mark.django_db
def test_basket_update_qty_min(create_product, create_basket):
    """测试修改购物车数据数量少于1"""
    product_id = create_product.id
    product_qty = 0
    url = reverse("basket:basket_update")
    payload = {"product_id": product_id, "product_qty": product_qty}
    response = create_basket.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json() == {"status": "error", "message": "数量非法"}


@pytest.mark.django_db
def test_basket_update_qty_error(create_product, create_basket):
    """测试修改购物车数据数量错误"""
    product_id = create_product.id
    product_qty = "abc"
    url = reverse("basket:basket_update")
    payload = {"product_id": product_id, "product_qty": product_qty}
    response = create_basket.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "error"


@pytest.mark.django_db
def test_basket_delete_success(create_product, create_basket):
    product_id = create_product.id
    url = reverse("basket:basket_delete")
    payload = {"product_id": product_id}
    response = create_basket.post(
        url, json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    res_data = response.json()
    assert response.json() == {
        "status": "success",
        "message": "数据成功删除",
        "category_count": 0,
    }
