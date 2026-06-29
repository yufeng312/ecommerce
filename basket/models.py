


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
        向购物车中添加商品,并修改对应的session值
        """
        product_id = str(product.id)

        if product_id not in self.basket:
            self.basket[product_id] = {'price': str(product.price), 'qty': int(qty)}
        else:
            self.basket[product_id]['qty'] += int(qty)

        self.session.modified = True

    def __len__(self):
        """
        返回购物车中的商品总数
        """
        return sum(int(item.get('qty', 0)) for item in self.basket.values())