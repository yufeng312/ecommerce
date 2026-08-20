import pytest

from order.tasks import cancel_unpaid_order_task


@pytest.mark.django_db
def test_cancel_unpaid_order_success(
    create_user, create_order, create_product, create_order_item
):
    """测试成功取消订单并归还库存"""
    result = cancel_unpaid_order_task(create_order.order_sn)
    assert "系统自动取消并归还库存" in result
    create_order.refresh_from_db()
    assert create_order.status == 50
    create_product.refresh_from_db()
    assert create_product.stock == 15


@pytest.mark.django_db
def test_cancel_unpaid_order_status_20(
    create_user, create_order, create_product, create_order_item
):
    """测试订单状态为20,跳过取消订单"""
    create_order.status = 20
    create_order.save()
    result = cancel_unpaid_order_task(create_order.order_sn)
    assert "状态非待付款,跳过自动取消" in result
    create_order.refresh_from_db()
    assert create_order.status == 20
    create_product.refresh_from_db()
    assert create_product.stock == 10


@pytest.mark.django_db
def test_cancel_unpaid_exception(
    mocker, create_user, create_order, create_product, create_order_item
):
    """测试发生异常"""
    mocker.patch(
        "order.models.Order.objects.select_for_update",
        side_effect=Exception("数据库锁超时"),
    )
    result = cancel_unpaid_order_task(create_order.order_sn)
    assert "数据库锁超时" in result
