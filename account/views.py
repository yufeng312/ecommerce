from django.shortcuts import (render, redirect, get_object_or_404)
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import (login, logout)
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.http import (urlsafe_base64_decode, urlsafe_base64_encode)
from django.utils.encoding import (force_bytes, force_str)

from .models import User
from order.models import Order
from .tokens import account_activation_token
from .forms import (RegistrationForm, UserEditForm)


@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_time')
    return render(request, 'account/user/dashboard.html', {'orders': orders})

@login_required
def edit_details(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST, files=request.FILES)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request, 'account/user/edit_details.html', {'user_form': user_form})

@login_required
def delete_user(request):
    user = request.user
    user.is_active = False
    user.save()
    logout(request)
    return redirect('account:delete_confirmation')

def account_register(request):
    if request.method == 'POST':
        register_form = RegistrationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.email = register_form.cleaned_data['email']
            user.set_password(register_form.cleaned_data['password'])
            user.is_active = False
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activate_url = request.build_absolute_uri(
                reverse('account:activate', kwargs={'uid': uid, 'token': token})
            )
            subject = '激活你的账号'
            message = render_to_string('account/registration/account_registration_email.html', {
                'user': user,
                'activate_url': activate_url
            })
            user.email_user(subject=subject, message=message)
            return HttpResponse('账号注册成功,请前往邮箱激活账号')
    else:
        register_form = RegistrationForm()
    return render(request, 'account/registration/register.html', {'form': register_form})

def account_activate(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('account:dashboard')
    else:
        return render(request, 'account/registration/activation_invalid.html')
