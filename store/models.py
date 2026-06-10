from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        db_table = 'Category'
        verbose_name = '商品类型'
        verbose_name_plural = '商品类型'

    def __str__(self):
        return self.name


class Product(models.Model):
    SCORE_CHOICES = [
        (0.0, '0.0分'), (0.5, '0.5分'), (1.0, '1.0分'), (1.5, '1.5分'), 
        (2.0, '2.0分'), (2.5, '2.5分'), (3.0, '3.0分'), (3.5, '3.5分'), 
        (4.0, '4.0分'), (4.5, '4.5分'), (5.0, '5.0分'), 
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    description = models.TextField()
    product_code = models.CharField(max_length=255, unique=True , blank=False, null=False)
    stock = models.PositiveIntegerField(default=0)
    score = models.FloatField(default=3.0, choices=SCORE_CHOICES)
    is_discount = models.BooleanField(default=False)
    discount = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default='1.00',
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))]
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def discount_price(self):
        if self.is_discount:
            return round(self.price * self.discount, 2)
        return self.price

    class Meta:
        db_table = 'Product'
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-create_time']
    
    def __str__(self):
        return self.name
