from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from .forms import (UserLoginForm, PwdForgotForm, PwdForgotConfirmForm)
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.account_register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html', 
                                                form_class=UserLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/account/login/'), name='logout'),
    path('activate/<slug:uid>/<slug:token>/', views.account_activate, name='activate'),
    path('password_forgot/', auth_views.PasswordResetView.as_view(template_name='account/password_forgot/password_forgot_form.html',
                                                                success_url=reverse_lazy('account:password_forgot_done'),
                                                                email_template_name='account/password_forgot/password_forgot_email.html',
                                                                form_class=PwdForgotForm), name='password_forgot'),
    path('password_forgot_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_forgot/password_forgot_confirm.html',
                                                                                                success_url=reverse_lazy('account:password_forgot_complate'),
                                                                                                form_class=PwdForgotConfirmForm), name='password_forgot_confirm'),                                                            
    path('password_forgot_done/', TemplateView.as_view(template_name='account/password_forgot/password_forgot_done.html'), name='password_forgot_done'),
    path('password_forgot_complate/', TemplateView.as_view(template_name='account/password_forgot/password_forgot_complate.html'), name='password_forgot_complate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_details, name='edit_details'),
    path('profile/delete_user/', views.delete_user, name='delete_user'),
    path('profile/delete_confirm/', TemplateView.as_view(template_name='account/dashboard/delete_confirm.html'), 
        name='delete_confirmation'),
]
