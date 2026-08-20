import uuid

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from account.models import Address, User
from account.tokens import account_activation_token


@pytest.mark.django_db
def test_dashboard_success(client, create_order, create_user):
    """测试成功渲染个人中心所有订单"""
    client.force_login(create_user)
    url = reverse("account:dashboard") + "?page=1&status=all"
    response = client.get(url)
    assert response.status_code == 200
    assert create_order in response.context["orders"]
    assert "all" == response.context["current_status"]


@pytest.mark.django_db
def test_dashboard_success_status_10(client, create_order, create_user):
    """测试渲染个人中心中订单状态为10的订单"""
    client.force_login(create_user)
    url = reverse("account:dashboard") + "?page=1&status=10"
    response = client.get(url)
    assert response.status_code == 200
    assert create_order in response.context["orders"]
    assert "10" == response.context["current_status"]


@pytest.mark.django_db
def test_dashboard_status_error(client, create_order, create_user):
    """测试渲染个人中心中订单状态错误时,修改为all"""
    client.force_login(create_user)
    url = reverse("account:dashboard") + "?page=1&status=aaa"
    response = client.get(url)
    assert response.status_code == 200
    assert create_order in response.context["orders"]
    assert "all" == response.context["current_status"]


@pytest.mark.django_db
def test_edit_details_success(client, create_user):
    """测试成功修改用户信息"""
    client.force_login(create_user)
    data = {"username": "aaaa", "phone": "13122222222", "description": "aaa"}
    url = reverse("account:edit_details")
    response = client.post(url, data=data)
    assert response.status_code == 200
    create_user.refresh_from_db()
    assert create_user.username == "aaaa"
    assert create_user.phone == "13122222222"
    assert create_user.description == "aaa"


@pytest.mark.django_db
def test_get_edit_details(client, create_user):
    """测试修改用户信息页面get请求"""
    client.force_login(create_user)
    url = reverse("account:edit_details")
    response = client.get(url)
    assert response.status_code == 200
    user_form = response.context["user_form"]
    assert create_user.username == user_form["username"].value()
    assert create_user.email == user_form["email"].value()


@pytest.mark.django_db
def test_delete_user_success(client, create_user):
    """测试成功注销用户"""
    client.force_login(create_user)
    url = reverse("account:delete_user")
    response = client.post(url)
    assert response.status_code == 302
    create_user.refresh_from_db()
    assert create_user.is_active == False


@pytest.mark.django_db
def test_account_register_success(client):
    """测试成功注册"""
    data = {
        "username": "cccc",
        "email": "c@c.com",
        "password": "adminpwww312",
        "password2": "adminpwww312",
    }
    url = reverse("account:register")
    response = client.post(url, data=data)
    assert response.status_code == 200
    user = User.objects.filter(username="cccc").first()
    assert user.username == "cccc"
    assert user.email == "c@c.com"
    assert user.is_active == False


@pytest.mark.django_db
def test_get_account_register(client):
    """测试注册页面get请求"""
    url = reverse("account:register")
    response = client.get(url)
    assert response.status_code == 200
    assert "username" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_account_activate_success(client):
    """测试成功激活用户"""
    user = User.objects.create_user(
        username="testuser",
        email="test@test.com",
        password="testpw312",
        is_active=False,
    )
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    url = reverse("account:activate", args=[uid, token])
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("account:dashboard")
    user.refresh_from_db()
    assert user.is_active == True


@pytest.mark.django_db
def test_account_activate_user_is_none(client):
    """测试激活用户时用户不存在"""
    uid = "aaabbb"
    invalid_token = "cccddd"
    url = reverse("account:activate", args=[uid, invalid_token])
    response = client.get(url)
    assert response.status_code == 200
    assert "account/registration/activation_invalid.html" in [
        t.name for t in response.templates
    ]


@pytest.mark.django_db
def test_address_view_success(client, create_user, create_address):
    """测试用户地址页面"""
    client.force_login(create_user)
    url = reverse("account:address_view")
    response = client.get(url)
    assert response.status_code == 200
    assert create_address in response.context["addresses"]


@pytest.mark.django_db
def test_address_add_success(client, create_user, create_address):
    """测试成功添加用户地址"""
    client.force_login(create_user)
    data = {
        "phone": "13166666666",
        "name": "eeee",
        "province": "山东省",
        "city": "青岛市",
        "district": "崂山区",
        "detail_address": "松岭路",
    }
    url = reverse("account:address_add")
    response = client.post(url, data=data)
    assert response.status_code == 302
    assert response.url == reverse("account:address_view")
    address = Address.objects.filter(name="eeee").first()
    assert address is not None
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "地址添加成功" in messages


@pytest.mark.django_db
def test_get_address_add_success(client, create_user, create_address):
    """测试添加用户地址get请求"""
    client.force_login(create_user)
    url = reverse("account:address_add")
    response = client.get(url)
    assert response.status_code == 200
    assert "account/address/address_add.html" in [t.name for t in response.templates]
    assert "detail_address" in response.content.decode("utf-8")


@pytest.mark.django_db
class TestAddressEditView:
    def test_address_edit_success(self, client, create_user, create_address):
        """测试成功修改用户地址"""
        client.force_login(create_user)
        data = {
            "phone": "13166666666",
            "name": "eeee",
            "province": "山东省",
            "city": "青岛市",
            "district": "崂山区",
            "detail_address": "松岭路",
        }
        url = reverse("account:address_edit", args=[create_address.id])
        response = client.post(url, data=data)
        assert response.status_code == 302
        assert response.url == reverse("account:address_view")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "地址修改成功" in messages
        create_address.refresh_from_db()
        assert create_address.name == "eeee"
        assert create_address.detail_address == "松岭路"

    def test_address_is_none(self, client, create_user, create_address):
        """测试修改的用户地址不存在"""
        client.force_login(create_user)
        uid = uuid.uuid4()
        url = reverse("account:address_edit", args=[uid])
        response = client.post(url)
        assert response.status_code == 302
        assert response.url == reverse("account:address_view")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "地址不存在" in messages

    def test_get_address_edit_success(self, client, create_user, create_address):
        """测试修改用户地址get请求"""
        client.force_login(create_user)
        url = reverse("account:address_edit", args=[create_address.id])
        response = client.get(url)
        assert response.status_code == 200
        assert create_address == response.context["address"]


@pytest.mark.django_db
def test_address_delete_success(client, create_user, create_address):
    """测试成功删除用户地址,第二个地址自动变为默认地址"""
    client.force_login(create_user)
    address = Address.objects.create(
        user=create_user,
        name="李四",
        phone="13177777777",
        province="山东省",
        city="青岛市",
        district="李沧区",
        detail_address="苗岭路",
        is_default=False,
    )
    address.save()
    url = reverse("account:address_delete", args=[create_address.id])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("account:address_view")
    assert not Address.objects.filter(id=create_address.id).exists()
    address.refresh_from_db()
    assert address.is_default == True


@pytest.mark.django_db
def test_delete_address_is_none(client, create_user, create_address):
    """测试删除的用户地址不存在"""
    client.force_login(create_user)
    uid = uuid.uuid4()
    url = reverse("account:address_delete", args=[uid])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("account:address_view")
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "地址不存在或已被删除" in messages


@pytest.mark.django_db
def test_address_default_success(client, create_user, create_address):
    """测试成功设置用户地址为默认地址"""
    client.force_login(create_user)
    address = Address.objects.create(
        user=create_user,
        name="李四",
        phone="13177777777",
        province="山东省",
        city="青岛市",
        district="李沧区",
        detail_address="苗岭路",
        is_default=False,
    )
    address.save()
    url = reverse("account:address_default", args=[address.id])
    response = client.post(url)
    assert response.status_code == 302
    address.refresh_from_db()
    assert address.is_default == True
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "默认地址设置成功" in messages


@pytest.mark.django_db
def test_address_default_is_none(client, create_user, create_address):
    """测试设置默认地址的用户地址不存在"""
    client.force_login(create_user)
    uid = uuid.uuid4()
    url = reverse("account:address_default", args=[uid])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("account:address_view")
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "地址不存在" in messages


@pytest.mark.django_db
def test_wishlist_success(client, create_user, create_product):
    """测试加载收藏页面"""
    client.force_login(create_user)
    url = reverse("account:wishlist")
    response = client.get(url)
    assert response.status_code == 200
    assert create_product in response.context["wishlist"]


@pytest.mark.django_db
def test_wishlist_add_remove_success(client, create_user, create_product):
    """测试成功将收藏的商品移除"""
    client.force_login(create_user)
    url = reverse("account:wishlist_add", args=[create_product.id])
    response = client.post(url)
    assert response.status_code == 302
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "测试商品已从我的收藏中移除" in messages


@pytest.mark.django_db
def test_wishlist_add_success(client, create_user, create_product):
    """测试成功添加产品到我的收藏"""
    client.force_login(create_user)
    create_product.user_wishlist.remove(create_user)
    url = reverse("account:wishlist_add", args=[create_product.id])
    response = client.post(url)
    assert response.status_code == 302
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "测试商品已添加到我的收藏" in messages
