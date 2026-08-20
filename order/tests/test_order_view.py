import pytest
from django.conf import settings
from django.contrib.messages import get_messages
from django.urls import reverse

from order.models import Order


@pytest.mark.django_db
def test_order_confirm_success(create_basket, create_user, create_address):
    """测试订单确认页"""
    create_basket.force_login(create_user)
    url = reverse("order:order_confirm")
    response = create_basket.get(url)
    assert response.status_code == 200
    assert create_address in response.context["addresses"]
    assert response.context["user"] == create_user
    assert response.context["default_address"] == create_address


@pytest.mark.django_db
class TestOrderCreateView:
    @pytest.mark.django_db
    def test_get_order_create_success(self, client, create_user):
        """测试创建订单页面get请求"""
        client.force_login(create_user)
        url = reverse("order:order_create")
        response = client.get(url)
        assert response.status_code == 302

    def test_order_create_success(
        self, create_basket, create_product, create_user, create_address
    ):
        """测试正常创建订单并扣减库存"""
        create_basket.force_login(create_user)
        url = reverse("order:order_create")
        response = create_basket.post(url, data={"address_id": create_address.id})

        create_product.refresh_from_db()
        assert response.status_code == 302
        assert create_product.stock == 8
        order = Order.objects.get(user=create_user)
        assert order.recipient_name == "张三"
        assert order.status == 10

    @pytest.mark.django_db
    def test_order_create_out_of_stock(
        self, create_basket, create_product, create_user, create_address
    ):
        """测试超出库存,无法扣减"""
        create_basket.force_login(create_user)
        session = create_basket.session
        session["basket"][str(create_product.id)]["qty"] = 100
        session.save()
        url = reverse("order:order_create")
        response = create_basket.post(
            url, data={"address_id": create_address.id}, follow=True
        )

        assert response.status_code == 200
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert any("库存不足" in msg for msg in messages)
        assert Order.objects.count() == 0

    @pytest.mark.django_db
    def test_order_create_blank_basket(
        self, create_basket, create_product, create_user, create_address
    ):
        """测试购物车为空"""
        create_basket.force_login(create_user)
        session = create_basket.session
        del session["basket"][str(create_product.id)]
        session.save()
        url = reverse("order:order_create")
        response = create_basket.post(url, data={"address_id": create_address.id})
        assert response.status_code == 302
        assert response.url == reverse("basket:basket_summary")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "您的购物车空空如也,无法下单" in messages
        assert Order.objects.count() == 0

    @pytest.mark.django_db
    def test_order_create_product_miss(
        self, create_basket, create_product, create_user, create_address
    ):
        """测试商品下架"""
        create_basket.force_login(create_user)
        create_product.is_active = False
        create_product.save()
        url = reverse("order:order_create")
        response = create_basket.post(url, data={"address_id": create_address.id})
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert response.status_code == 302
        assert any("部分商品已下架或不存在" in msg for msg in messages)
        assert Order.objects.count() == 0

    @pytest.mark.django_db
    def test_order_create_exception(
        self, mocker, create_basket, create_product, create_user, create_address
    ):
        """测试商品下架"""
        create_basket.force_login(create_user)
        mocker.patch(
            "order.views.Order.objects.create", side_effect=Exception("模拟未知异常")
        )
        url = reverse("order:order_create")
        response = create_basket.post(url, data={"address_id": create_address.id})
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert response.status_code == 302
        assert "系统繁忙,订单创建失败,请稍后重试" in messages
        assert Order.objects.count() == 0

    @pytest.mark.django_db
    def test_order_create_order_is_none(
        self, mocker, create_basket, create_product, create_user, create_address
    ):
        """测试订单创建失败"""
        create_basket.force_login(create_user)
        mocker.patch("order.views.Order.objects.create", return_value=None)
        mocker.patch("order.views.OrderItem.objects.bulk_create")
        url = reverse("order:order_create")
        response = create_basket.post(url, data={"address_id": create_address.id})
        assert response.status_code == 302
        assert response.url == reverse("basket:basket_summary")


@pytest.mark.django_db
def test_order_cancel_success(
    client, create_order, create_user, create_order_item, create_product
):
    """测试成功取消订单,并恢复库存"""
    client.force_login(create_user)
    url = reverse("order:order_cancel", args=[create_order.order_sn])
    response = client.post(url)
    create_product.refresh_from_db()
    create_order.refresh_from_db()
    assert create_order.status == 50
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "订单已成功取消" in messages
    assert create_product.stock == 15


@pytest.mark.django_db
def test_order_cancel_status_40(
    client, create_order, create_user, create_order_item, create_product
):
    """测试状态已被取消,无法继续取消"""
    client.force_login(create_user)
    create_order.status = 40
    create_order.save()
    url = reverse("order:order_cancel", args=[create_order.order_sn])
    response = client.post(url)
    create_product.refresh_from_db()
    create_order.refresh_from_db()
    assert create_order.status == 40
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "该订单无法取消或已处理" in messages
    assert create_product.stock == 10


@pytest.mark.django_db
def test_order_detail_success(
    client, create_order, create_user, create_order_item, create_product
):
    """测试订单详情页"""
    client.force_login(create_user)
    url = reverse("order:order_detail", args=[create_order.order_sn])
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["order"] == create_order
    assert create_order_item in response.context["order_items"]


@pytest.mark.django_db
class TestAlipayPayView:
    def test_alipay_pay_view_success(self, mocker, client, create_user, create_order):
        """测试成功生成支付宝链接并重定向"""
        client.force_login(create_user)
        mock_alipay_client = mocker.MagicMock()
        mock_alipay_client.api_alipay_trade_page_pay.return_value = (
            "out_trade_no=123&sign=xxx"
        )
        mocker.patch("order.views.get_alipay_client", return_value=mock_alipay_client)
        url = reverse("order:alipay_pay", args=[create_order.order_sn])
        response = client.get(url)
        assert response.status_code == 302
        expected_url = f"{settings.ALIPAY_GATEWAY_URL}?out_trade_no=123&sign=xxx"
        assert response.url == expected_url

    def test_alipay_pay_exception_error(
        self, mocker, client, create_user, create_order
    ):
        """测试初始化失败"""
        client.force_login(create_user)
        mocker.patch("order.views.get_alipay_client", side_effect=Exception("解析失败"))
        url = reverse("order:alipay_pay", args=[create_order.order_sn])
        response = client.get(url)
        assert response.status_code == 500
        assert "支付宝初始化失败" in response.content.decode("utf-8")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "系统繁忙,请稍后重试" in messages


@pytest.mark.django_db
def test_alipay_return_success(mocker, client):
    """测试验签成功,跳转到返回页"""
    mock_alipay = mocker.MagicMock()
    mock_alipay.verify.return_value = True
    mocker.patch("order.views.get_alipay_client", return_value=mock_alipay)

    params = {
        "out_trade_no": "20260819001",
        "trade_no": "20260819001001",
        "total_amount": "99.00",
        "sign": "fake_sign",
    }
    url = reverse("order:alipay_return")
    response = client.get(url, data=params)

    assert response.status_code == 200
    assert response.context["out_trade_no"] == "20260819001"
    assert response.context["trade_no"] == "20260819001001"
    assert response.context["total_amount"] == "99.00"


@pytest.mark.django_db
def test_alipay_return_error(mocker, client):
    """测试验签失败"""
    mock_alipay = mocker.MagicMock()
    mock_alipay.verify.return_value = False
    mocker.patch("order.views.get_alipay_client", return_value=mock_alipay)

    url = reverse("order:alipay_return")
    response = client.get(url)

    assert response.status_code == 400
    assert "支付校验失败" in response.content.decode("utf-8")


@pytest.mark.django_db
class TestAlipayNotifyView:
    def test_alipay_notify_success(self, mocker, client, create_user, create_order):
        """测试异步验签成功,成功修改订单状态"""
        client.force_login(create_user)
        mock_alipay = mocker.MagicMock()
        mock_alipay.get_alipay_client.verify.return_value = True
        mocker.patch("order.views.get_alipay_client", return_value=mock_alipay)
        params = {
            "out_trade_no": "20260810220238000017634",
            "trade_no": "20160819001",
            "total_amount": "50.00",
            "sign": "fake_sign",
            "trade_status": "TRADE_SUCCESS",
        }
        url = reverse("order:alipay_notify")
        response = client.post(url, data=params)
        assert response.status_code == 200
        assert "success" in response.content.decode("utf-8")
        create_order.refresh_from_db()
        assert create_order.status == 20
        assert create_order.trade_no == "20160819001"

    @pytest.mark.django_db
    def test_alipay_notify_success_status_20(
        self, mocker, client, create_user, create_order
    ):
        """测试异步验签成功,订单状态20,返回success"""
        client.force_login(create_user)
        mock_alipay = mocker.MagicMock()
        mock_alipay.get_alipay_client.verify.return_value = True
        mocker.patch("order.views.get_alipay_client", return_value=mock_alipay)
        create_order.status = 20
        create_order.save()
        params = {
            "out_trade_no": "20260810220238000017634",
            "trade_no": "20160819001",
            "total_amount": "50.00",
            "sign": "fake_sign",
            "trade_status": "TRADE_SUCCESS",
        }
        url = reverse("order:alipay_notify")
        response = client.post(url, data=params)
        assert response.status_code == 200
        assert "success" in response.content.decode("utf-8")

    def test_alipay_notify_order_not_exists(self, mocker, client, create_user):
        """测试异步验签成功,成功修改订单状态"""
        client.force_login(create_user)
        mock_alipay = mocker.MagicMock()
        mock_alipay.get_alipay_client.verify.return_value = True
        mocker.patch("order.views.get_alipay_client", return_value=mock_alipay)
        params = {
            "out_trade_no": "20260810220238000017634",
            "trade_no": "20160819001",
            "total_amount": "50.00",
            "sign": "fake_sign",
            "trade_status": "TRADE_SUCCESS",
        }
        url = reverse("order:alipay_notify")
        response = client.post(url, data=params)
        assert response.status_code == 200
        assert "fail" in response.content.decode("utf-8")

    def test_alipay_notify_fail(self, mocker, client, create_user, create_order):
        """测试异步验签失败"""
        client.force_login(create_user)
        mock_alipay = mocker.MagicMock()
        mock_alipay.get_alipay_client.verify.return_value = True
        mocker.patch("order.views.get_alipay_client", return_value=mock_alipay)
        params = {
            "out_trade_no": "20260810220238000017634",
            "trade_no": "20160819001",
            "total_amount": "50.00",
            "sign": "fake_sign",
            "trade_status": "TRADE_FAIL",
        }
        url = reverse("order:alipay_notify")
        response = client.post(url, data=params)
        assert response.status_code == 200
        assert "fail" in response.content.decode("utf-8")
        create_order.refresh_from_db()
        assert create_order.status == 10
