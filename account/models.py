from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,  
                                        PermissionsMixin)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password, **other_fields):
        if not email:
            raise ValueError('必须填写邮箱地址')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, username, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_superuser', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置is_staff=True')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置is_superuser=True')
        
        return self.create_user(email, username, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True)
    username = models.CharField(max_length=200, unique=True, blank=False)
    avatar = models.ImageField('avatar', upload_to='avatar', blank=True)
    phone = models.CharField(max_length=16, blank=True)
    description = models.TextField(max_length=300 , blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'User'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            '1@1.com',
            [self.email],
            fail_silently=False
        )

    def __str__(self):
        return self.email

