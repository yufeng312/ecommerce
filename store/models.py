from decimal import ROUND_HALF_UP, Decimal

from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class ProductManager(models.Manager):
    """自定义商品管理器.查询可用商品"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


# 商品分类模型
class Category(MPTTModel):
    """使用MPTT的商品分类表,对应商品大的分类"""

    name = models.CharField(
        verbose_name='商品分类名称',
        max_length=255, 
        unique=True
    )
    slug = models.SlugField(
        max_length=255, 
        unique=True
    )
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        db_table = "Category"
        verbose_name = "商品分类"
        verbose_name_plural = "商品分类"

    def get_absolute_url(self):
        return reverse('store:category_product', args=[self.slug])

    def __str__(self):
        return self.name

# 商品类型模型
class ProductType(models.Model):
    """商品类型表.用来绑定某种类型对应的产品规格和属性."""

    name = models.CharField(
        verbose_name='商品类型名称',
        max_length=255,
        unique=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'productType'
        verbose_name = '商品类型'
        verbose_name_plural = '商品类型'

    def __str__(self):
        return self.name

# 商品规格
class ProductSpecification(models.Model):
    """商品规格表.一种商品类型具有的规格和属性"""

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)  # 阻止删除
    name = models.CharField(
        verbose_name='名称',
        max_length=255
    )

    class Meta:
        db_table = 'ProductSpecification'
        verbose_name = '商品规格'
        verbose_name_plural = '商品规格'

    def __str__(self):
        return self.name

# 商品模型
class Product(models.Model):
    """商品表"""

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    category = models.ForeignKey(
        Category, on_delete=models.RESTRICT, related_name="products"
    )
    name = models.CharField(
        verbose_name='商品名称',
        max_length=255, 
        unique=True, 
        null=False, 
        blank=False
    )
    slug = models.SlugField(max_length=255, unique=True)
    price = models.DecimalField(
        verbose_name='商品原价',
        max_digits=10, 
        decimal_places=2, 
        default=Decimal("0.00")
    )
    description = models.TextField(verbose_name='商品描述', blank=True )
    stock = models.PositiveIntegerField(verbose_name='库存', default=0)
    is_discount = models.BooleanField(verbose_name='是否打折', default=False)
    is_active = models.BooleanField(default=True)
    discount = models.DecimalField(
        verbose_name='折扣率',
        max_digits=3,  # 最大3位数字
        decimal_places=2,  # 小数点后获取2位
        default=Decimal("1.00"),
        # 最大值为1.00,最小值为0.00
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("1.00")),
        ],
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    products = ProductManager()

    @property
    def discount_price(self):
        """获取商品打折后的价格"""
        if self.is_discount:
            # 精度保留两位小数,ROUND_HALF_UP采用传统的四舍五入
            return (self.price * self.discount).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return self.price

    @property
    def feature_image_url(self):
        """获取商品主图URL,没有主图则获取第一张图片,没有图片则获取默认图片"""
        image_obj = self.product_image.filter(is_feature=True).first() or self.product_image.first()
        if image_obj and image_obj.image:
            return image_obj.image.url
        return 'images/default.png'

    @property
    def feature_alt_text(self):
        """获取商品主图的alt描述,没有则返回商品名称"""
        image_obj = self.product_image.filter(is_feature=True).first() or self.product_image.first()
        if image_obj and image_obj.alt_text:
            return image_obj.alt_text
        return self.name or '暂无商品图'

    class Meta:
        db_table = "Product"
        verbose_name = "商品"
        verbose_name_plural = "商品"
        # 按创建时间降序排列
        ordering = ["-create_time"]

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.category.slug, self.slug])
    
    def __str__(self):
        return self.name

class ProductSpecificationValue(models.Model):
    """商品属性表.商品规格具体的数值"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.ForeignKey(ProductSpecification, on_delete=models.RESTRICT)
    value = models.CharField(
        verbose_name='属性值',
        max_length=255
    )

    class Meta:
        db_table = 'ProductSpecificationValue'
        verbose_name = "商品属性"
        verbose_name_plural = "商品属性"

    def __str__(self):
        return self.value

class ProductImage(models.Model):
    """商品图片表"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    image = models.ImageField(
        verbose_name='商品图片',
        upload_to='images',
        default='images/default.png'
    )
    alt_text = models.CharField(
        verbose_name='图片描述',
        max_length=255,
        null=True,
        blank=True
    )
    is_feature = models.BooleanField(verbose_name='商品主图', default=False)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ProductImage'
        verbose_name = "商品图片"
        verbose_name_plural = "商品图片"
