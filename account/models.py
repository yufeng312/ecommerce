import uuid

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.mail import send_mail
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password, **other_fields):
        if not email:
            raise ValueError("必须填写邮箱地址")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_active", True)
        other_fields.setdefault("is_superuser", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置is_staff=True")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置is_superuser=True")

        return self.create_user(email, username, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email", unique=True)
    username = models.CharField(max_length=200, unique=True, blank=False)
    avatar = models.ImageField("avatar", upload_to="avatar", blank=True)
    phone = models.CharField(max_length=16, blank=True)
    description = models.TextField(max_length=300, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "User"
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def email_user(self, subject, message):
        send_mail(subject, message, "1@1.com", [self.email], fail_silently=False)

    def __str__(self):
        return self.email


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="用户",
    )
    name = models.CharField(max_length=50, verbose_name="收件人姓名", blank=False)
    phone = models.CharField(max_length=11, verbose_name="收件人手机号", blank=False)
    province = models.CharField(max_length=50, verbose_name="省份", blank=False)
    city = models.CharField(max_length=50, verbose_name="城市", blank=False)
    district = models.CharField(max_length=50, verbose_name="区/县", blank=False)
    detail_address = models.CharField(
        max_length=255, verbose_name="详细地址", blank=False
    )
    is_default = models.BooleanField(
        default=False, db_index=True, verbose_name="是否为默认地址"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "Address"
        verbose_name = "地址簿"
        verbose_name_plural = "地址簿"
        ordering = ["-is_default", "-update_time"]

    def __str__(self):
        return "收货地址"

    def save(self, *args, **kwargs):
        """
        1.如果用户第一次保存地址,自动设为默认地址
        2.如果修改默认地址,自动将其他地址设为非默认,保证一个用户只有一个默认地址
        """
        if not Address.objects.filter(user=self.user).exists():
            self.is_default = True
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        super().save(*args, **kwargs)
