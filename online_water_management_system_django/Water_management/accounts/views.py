from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from database.models import Products, CustomerPrices
from .forms import CustomerRegisterForm, CorporateRegisterForm

from django.conf import settings

base_dir = settings.BASE_DIR


def register_user(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/home/')
        elif request.user.is_customer:
            return redirect('/customer/home/')
        elif request.user.is_employee:
            return redirect('/employee/home')
    else:
        context = {}
        if request.POST:
            form = CustomerRegisterForm(request.POST)
            form.ConfirmPassword = request.POST.get('ConfirmPassword')
            if form.is_valid():
                customer = form.save()
                price_list = []
                for products in Products.objects.all():
                    price = CustomerPrices(product=products, price=products.price)
                    price.save()
                    price_list.append(price)
                customer.discounted_price.set(price_list)
                customer.save()
                return render(request, 'accounts/approval.html')
            else:
                context['form'] = form
        else:
            context['form'] = CustomerRegisterForm
        return render(request, 'accounts/register.html', context)


def login_user(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/home/')
        elif request.user.is_customer:
            return redirect('/customer/home/')
        elif request.user.is_employee:
            return redirect('/employee/home')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['pass']
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_available:
                    if user.is_approved:
                        login(request, user)
                        if user.is_customer:
                            return redirect('/customer/home/')
                        if user.is_employee:
                            return redirect('/employee/home/')
                        if user.is_superuser:
                            return redirect('/admin/home/')
                    else:
                        return render(request, 'accounts/approval.html')
                else:

                    HttpResponseNotFound(status=404)

            else:
                context['error'] = 'Invalid Credentials'
                return render(request, 'accounts/login.html', context)
        else:
            return render(request, 'accounts/login.html')


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/home/')
    else:
        return HttpResponseNotFound(status=404)


def register_corporate(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/home/')
        elif request.user.is_customer:
            return redirect('/customer/home/')
        elif request.user.is_employee:
            return redirect('/employee/home')
    else:
        context = {}
        if request.POST:
            form = CorporateRegisterForm(request.POST)
            form.ConfirmPassword = request.POST.get('ConfirmPassword')
            if form.is_valid():
                customer = form.save()
                price_list = []
                for products in Products.objects.all():
                    price = CustomerPrices(product=products, price=products.price)
                    price.save()
                    price_list.append(price)
                customer.discounted_price.set(price_list)
                customer.save()
                return render(request, 'accounts/approval.html')
            else:
                context['form'] = form
        else:
            context['form'] = CorporateRegisterForm
        return render(request, 'accounts/register_corporate.html', context)
