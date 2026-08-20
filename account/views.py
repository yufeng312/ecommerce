from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from order.models import Order, OrderItem
from store.models import Product

from .forms import AddressForm, RegistrationForm, UserEditForm
from .models import Address, User
from .tokens import account_activation_token


@login_required
def dashboard(request):
    status = request.GET.get("status", "all")
    page_number = request.GET.get("page", 1)
    orders_query = (
        Order.objects.prefetch_related(
            Prefetch(
                "order_items",
                queryset=OrderItem.objects.select_related(
                    "product__category"
                ).prefetch_related("product__product_image"),
            )
        )
        .filter(user=request.user)
        .order_by("-created_time")
    )
    if status != "all":
        try:
            orders_query = orders_query.filter(status=int(status))
        except ValueError:
            status = "all"
    paginator = Paginator(orders_query, 5)
    orders = paginator.get_page(page_number)
    unpaid_count = Order.objects.filter(user=request.user, status=10).count()
    page_range = paginator.get_elided_page_range(
        orders.number, on_each_side=3, on_ends=2
    )
    context = {
        "orders": orders,
        "current_status": status,
        "unpaid_count": unpaid_count,
        "page_range": page_range,
    }
    return render(request, "account/dashboard/dashboard.html", context=context)


@login_required
def edit_details(request):
    if request.method == "POST":
        user_form = UserEditForm(
            instance=request.user, data=request.POST, files=request.FILES
        )
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    return render(
        request, "account/dashboard/edit_details.html", {"user_form": user_form}
    )


@login_required
def delete_user(request):
    user = request.user
    user.is_active = False
    user.save()
    logout(request)
    return redirect("account:delete_confirmation")


def account_register(request):
    if request.method == "POST":
        register_form = RegistrationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.email = register_form.cleaned_data["email"]
            user.set_password(register_form.cleaned_data["password"])
            user.is_active = False
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activate_url = request.build_absolute_uri(
                reverse("account:activate", kwargs={"uid": uid, "token": token})
            )
            subject = "激活你的账号"
            message = render_to_string(
                "account/registration/account_registration_email.html",
                {"user": user, "activate_url": activate_url},
            )
            user.email_user(subject=subject, message=message)
            return render(
                request,
                "account/registration/register_email_confirm.html",
                {"email": user.email},
            )
    else:
        register_form = RegistrationForm()
    return render(
        request, "account/registration/register.html", {"form": register_form}
    )


def account_activate(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("account:dashboard")
    else:
        return render(request, "account/registration/activation_invalid.html")


@login_required
def address_view(request):
    addresses = Address.objects.filter(user=request.user).order_by(
        "-is_default", "-update_time"
    )
    return render(request, "account/address/address.html", {"addresses": addresses})


@login_required
def address_add(request):
    if request.method == "POST":
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "地址添加成功")
            return redirect("account:address_view")
    else:
        address_form = AddressForm()
    return render(request, "account/address/address_add.html", {"form": address_form})


@login_required
def address_edit(request, id):
    address_obj = Address.objects.filter(user=request.user, id=id).first()
    if not address_obj:
        messages.warning(request, "地址不存在")
        return redirect("account:address_view")
    if request.method == "POST":
        address_form = AddressForm(request.POST, instance=address_obj)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, "地址修改成功")
            return redirect("account:address_view")
    else:
        address_form = AddressForm(instance=address_obj)
    return render(
        request,
        "account/address/address_add.html",
        {"form": address_form, "address": address_obj},
    )


@login_required
def address_delete(request, id):
    address = Address.objects.filter(user=request.user, id=id).first()
    if address:
        was_default = address.is_default
        address.delete()
        if was_default:
            address_first = Address.objects.filter(user=request.user).first()
            if address_first:
                address_first.is_default = True
                address_first.save()
    else:
        messages.warning(request, "地址不存在或已被删除")
    return redirect("account:address_view")


@login_required
def address_default(request, id):
    address = Address.objects.filter(user=request.user, id=id).first()
    if not address:
        messages.error(request, "地址不存在")
        return redirect("account:address_view")
    address.is_default = True
    address.save()
    messages.success(request, "默认地址设置成功")
    return redirect("account:address_view")


@login_required
def wishlist(request):
    products = (
        Product.objects.filter(user_wishlist=request.user)
        .select_related("category")
        .prefetch_related("product_image")
    )
    return render(request, "account/dashboard/wishlist.html", {"wishlist": products})


@login_required
def wishlist_add(request, id):
    product = get_object_or_404(Product, id=id)
    if product.user_wishlist.filter(id=request.user.id).exists():
        product.user_wishlist.remove(request.user)
        messages.success(request, f"{product.name}已从我的收藏中移除")
    else:
        product.user_wishlist.add(request.user)
        messages.success(request, f"{product.name}已添加到我的收藏")
    return redirect(request.META.get("HTTP_REFERER", "store:index"))
