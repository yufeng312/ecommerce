import re

from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm, SetPasswordForm)

from .models import User


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': '用户名', 'id': 'login-username'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': '密码', 'id': 'login-password'}
    ))


class RegistrationForm(forms.ModelForm):

    username = forms.CharField(
        label='用户名', 
        min_length=4, 
        max_length=30, 
        help_text='必填项, 长度在4-30个字符之间',
        error_messages={
            'required': '用户名不能为空',
            'min_length': '用户名太短,不能少于4个字符',
            'max_length': '用户名太长,不能超过30个字符'
        }
    )
    email = forms.EmailField(
        label='电子邮箱', 
        max_length=100, 
        error_messages={
            'required': '抱歉,电子邮箱不能为空',
            'invalid': '请输入有效的邮箱地址'
        }
    )
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text='请输入8-20位密码,由数字和字母组成',
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码太短,不能少于8位',
            'max_length': '密码太长,不能超过20位'
        }
    )
    password2 = forms.CharField(
        label='重复密码',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            return username
        username = username.lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise forms.ValidationError('用户名已存在')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被使用')
        return email
        
    def clean_password(self):
        password = self.cleaned_data['password']
        if not re.match('^(?=.*[A-Za-z])(?=.*[\d])[A-Za-z\d]{8,20}$', password):
            raise forms.ValidationError('密码必须由字母和数字组成,长度在8-20位之间')
        return password
    
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('两次输入的密码不一致')
        return password2


class PwdForgotForm(PasswordResetForm):
    email = forms.EmailField(label='电子邮箱', max_length=200, widget=forms.TextInput(
        attrs={'placeholder': '请输入电子邮箱..'}
    ))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if not user:
            raise ValueError('无效的电子邮箱地址')
        return email
    

class PwdForgotConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='新密码', widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label='确认密码', widget=forms.PasswordInput
    )

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1 and self.user.check_password(new_password1):
            raise forms.ValidationError('新密码不能与旧密码相同')
        return new_password1


class UserEditForm(forms.ModelForm):

    email = forms.EmailField(
        label='电子邮箱(无法修改)', 
        max_length=100, 
        disabled=True,
    )
    username = forms.CharField(
        label='用户名', 
        min_length=4, 
        max_length=30, 
        help_text='必填项, 长度在4-30个字符之间',
        widget=forms.TextInput(
            attrs={'placeholder': '请输入用户名..'}
        )
    )
    avatar = forms.ImageField(label='头像', required=False)
    phone = forms.RegexField(
        r'^1[3-9]\d{9}$',
        label='手机号',
        required=False,
        error_messages={
            'invalid': '请输入正确的手机号'
        },
        widget=forms.TextInput(
            attrs={'placeholder': '请填写手机号..'}
        )
    )
    description = forms.CharField(
        label='个人介绍',
        max_length=300,
        required=False,
        widget=forms.Textarea(
            attrs={'placeholder': '介绍一下自己吧..'}
        )
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'avatar', 'phone', 'description')
