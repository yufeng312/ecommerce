from decimal import Decimal

from django.conf import settings

from store.models import Product


class Basket:
    def __init__(self, request):
        """
        初始化session数据
        """
        self.session = request.session
        self.basket = self.session.setdefault(settings.BASKET_SESSION_ID, {})

    def add(self, product, qty):
        """
        向购物车中添加商品,并将商品id和商品数量保存到session中
        """
        product_id = str(product.id)

        if product_id not in self.basket:
            self.basket[product_id] = {'qty': int(qty)}
        else:
            self.basket[product_id]['qty'] += int(qty)
        self.save()

    @property
    def category_count(self):
        """
        购物车中商品种类的数量
        """
        return len(self.basket.keys())
    
    @property
    def total_price(self):
        """
        购物车中商品的总价
        """
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)

        price = Decimal('0.00')
        for product in products:
            qty = self.basket[str(product.id)]['qty']
            price += qty * product.price
        return price
    
    @property
    def payment_price(self):
        """
        购物车中商品实际总价
        """
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        total_price = Decimal('0.00')
        for product in products:
            qty = self.basket[str(product.id)]['qty']
            total_price += qty * product.discount_price
        return total_price
    
    @property
    def freight(self):
        """
        获取运费,满99包邮,否则运费为10元
        """
        if self.payment_price >= Decimal('99.00'):
            return Decimal('0.00')
        return Decimal('10.00')
    
    @property
    def discount_price(self):
        """
        优惠总价
        """
        return self.total_price - self.payment_price
    
    @property
    def total_payable(self):
        """
        实际支付金额
        """
        return self.payment_price + self.freight
    
    def update(self, product, qty):
        """
        更新购物车中的商品数量
        """
        product_id = str(product.id)
        self.basket[product_id]['qty'] = int(qty)
        self.session.modified = True

    def delete(self, product_id):
        """
        删除购物车中的商品
        """
        product_id = str(product_id)
        del self.basket[product_id]
        self.save()

    def __iter__(self):
        """
        用session中的商品id获取商品数据,复制商品数据,生成一个可迭代对象
        """
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        basket = {k: v.copy() for k, v in self.basket.items()}

        for product in products:
            basket[str(product.id)]['product'] = product
        
        for item in basket.values():
            product = item['product']
            item['saved_amount'] = product.price - product.discount_price
            item['total_price'] = product.discount_price * item['qty']
            yield item

    def __len__(self):
        """
        购物车中的商品总数
        """
        return sum(int(item.get('qty', 0)) for item in self.basket.values())
    
    def save(self):
        self.session.modified = True
    
    def clear(self):
        del self.session[settings.BASKET_SESSION_ID]
        self.save()