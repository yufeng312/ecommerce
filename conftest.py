from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from account.models import Address
from order.models import Order, OrderItem
from store.models import Category, Product, ProductType

User = get_user_model()


@pytest.fixture
def create_user(db):
    """创建一个测试用户"""
    user = User.objects.create_user(
        username="testuser", email="test@test.com", password="testpw312", is_active=True
    )
    return user


@pytest.fixture
def create_category(db):
    """创建一个测试分类"""
    return Category.objects.create(name="测试分类", slug="test-category")


@pytest.fixture
def create_product_type(db):
    """创建一个测试商品类型"""
    return ProductType.objects.create(name="测试商品类型", is_active=True)


@pytest.fixture
def create_product(db, create_category, create_product_type, create_user):
    """创建一个测试商品"""
    product = Product.objects.create(
        product_type=create_product_type,
        category=create_category,
        name="测试商品",
        slug="test-product",
        price=Decimal("10.00"),
        stock=10,
        is_discount=True,
        is_active=True,
        discount=Decimal("0.80"),
    )
    product.user_wishlist.add(create_user)
    return product


@pytest.fixture
def create_address(db, create_user):
    """创建一个测试地址"""
    address = Address.objects.create(
        user=create_user,
        name="张三",
        phone="13115151616",
        province="山东省",
        city="青岛市",
        district="李沧区",
        detail_address="黑龙江中路75号",
        is_default=True,
    )
    return address


@pytest.fixture
def create_basket(client, create_product):
    """创建一个包含商品的测试购物车"""
    session = client.session
    session["basket"] = {str(create_product.id): {"qty": 2}}
    session.save()
    return client


@pytest.fixture
def create_order(client, create_user):
    """创建一个测试订单,状态为待付款"""
    order = Order.objects.create(
        user=create_user,
        order_sn="20260810220238000017634",
        status=10,
        recipient_name="张三",
        recipient_phone="13115151616",
        address="山东省青岛市李沧区黑龙江中路75号",
        total_price=Decimal("40.00"),
        freight=Decimal("10.00"),
        discount_price=Decimal("10.00"),
        payment_price=Decimal("50.00"),
    )
    return order


@pytest.fixture
def create_order_item(client, create_order, create_product):
    order_item = OrderItem.objects.create(
        order=create_order,
        product=create_product,
        product_name="测试商品",
        price=Decimal("8.00"),
        quantity=5,
        total_price=Decimal("40.00"),
    )
    return order_item
