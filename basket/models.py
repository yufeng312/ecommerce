from decimal import Decimal

from store.models import Product


class Basket():
    def __init__(self, request):
        """
        初始化session数据
        """
        self.session = request.session
        basket = self.session.get('skey')
        if 'skey' not in request.session:
            basket = self.session['skey'] = {}
        self.basket = basket

    def add(self, product, qty):
        """
        向购物车中添加商品,并将商品id和商品数量保存到session中
        """
        product_id = str(product.id)

        if product_id not in self.basket:
            self.basket[product_id] = {'qty': int(qty)}
        else:
            self.basket[product_id]['qty'] += int(qty)

        self.session.modified = True

    def get_total_price(self):
        """
        返回购物车所有商品总价
        """
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        total_price = Decimal('0.00')
        for product in products:
            qty = self.basket[str(product.id)]['qty']
            total_price += qty * product.discount_price
        return total_price
    
    def category_count(self):
        """
        返回商品种类的数量
        """
        return len(self.basket.keys())
    
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
        self.session.modified = True

    def __iter__(self):
        """
        用session中的商品id获取商品数据,复制商品数据,生成一个可迭代对象
        """
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]['product'] = product
        
        for item in basket.values():
            product = item['product']

            item['saved_amount'] = product.price - product.discount_price
            item['total_price'] = product.discount_price * item['qty']
            yield item

    def __len__(self):
        """
        返回购物车中的商品总数
        """
        return sum(int(item.get('qty', 0)) for item in self.basket.values())