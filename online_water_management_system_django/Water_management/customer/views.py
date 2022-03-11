from django.http import HttpResponseNotFound
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from database.models import Products, Order, Customer, Area, OrderDetail, Schedule, Asset
from ast import literal_eval
from .forms import OrderForm, OrderQuantityForm
from Admin.views import string_to_list, form_to_string


def home(request):
    if request.user.is_authenticated and request.user.is_customer:
        user = Customer.objects.get(username=request.user.username)

        context = {
            'user': user,
            'assets': user.assets.all(),
            'orders': Order.objects.filter(customer=request.user, delivered=False)
        }

        return render(request, 'customer/home.html', context)

    return render(request, 'home.html')


def view_order(request, order_id):
    if request.user.is_authenticated and not request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        customer = order.customer
        data = {'order': order, 'quantity': product_quantity_list(order.desc.all()), 'customer': customer}
        return render(request, 'customer/ordered.html', data)

    return HttpResponseNotFound()


def my_orders(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        orders = Order.objects.filter(customer=request.user).order_by('-ordered_at')
        context = {
            'orders': orders,
            'user': Customer.objects.get(username=request.user.username)
        }
        return render(request, 'customer/view_orders.html', context=context)


def order_confirmed(request):
    if request.POST and request.user.is_authenticated:
        data = request.session['data']
        order_ = Order(customer=Customer.objects.get(username=data['username']),
                       frequency=data['frequency'],
                       address=data['address'],
                       area=Area.objects.get(name=data['area_name'], city__city=data['city__city']),
                       price=data['price'])
        order_.save()
        set_order_description(order_, data['quantity'])
        request.session['data'] = None
        return redirect('customer_home')
    return HttpResponseNotFound()


def order(request):
    if request.user.is_authenticated and not request.user.is_superuser and not request.user.is_employee:
        if request.POST:
            orderForm = OrderForm(request.POST, username=request.user.username)
            customer = Customer.objects.get(username=request.user.username)
            quantityForm = OrderQuantityForm(request.POST)
            if orderForm.is_valid() and quantityForm.is_valid():
                quantity = form_to_string(quantityForm)
                if not has_quantity(quantity):
                    return render(request, 'customer/order_form.html',
                                  {'message': 'Invalid Data or Empty order!',
                                   'order_form': OrderForm(username=request.user.username),
                                   'quantity_form': OrderQuantityForm()})
                area = orderForm.cleaned_data['area'].split(',')
                if not can_place_order(string_to_list(quantity),
                                       Area.objects.get(name=area[0].strip(), city__city=area[1].strip())):
                    return render(request, 'customer/order_form.html',
                                  {'message': 'Order too large for selected area. Please reduce order!',
                                   'order_form': OrderForm(username=request.user.username),
                                   'quantity_form': OrderQuantityForm()})
                price = get_price(quantity, customer)
                if orderForm.cleaned_data['area'] != "%s" % customer.area and not orderForm.cleaned_data['address']:
                    return render(request, 'customer/order_form.html',
                                  {'message': 'Must Enter Address if area other than default is selected!',
                                   'order_form': OrderForm(username=request.user.username),
                                   'quantity_form': OrderQuantityForm()})

                if orderForm.cleaned_data['address'] and orderForm.cleaned_data['area']:
                    address = orderForm.cleaned_data.get('address')
                    selected_area = Area.objects.get(name=area[0].strip(), city__city=area[1].strip())
                else:
                    address = customer.address
                    selected_area = customer.area

                order_ = Order(customer=customer, frequency=orderForm.cleaned_data['order_type'],
                               address=address, area=selected_area, price=price)
                request.session['data'] = {
                    "username": request.user.username,
                    'frequency': orderForm.cleaned_data['order_type'],
                    "address": address,
                    'area_name': area[0].strip(),
                    'city__city': area[1].strip(),
                    'price': price,
                    "quantity": quantity
                }

                data = {'order': order_, 'quantity': get_product_quantity_map(quantity), 'customer': customer,
                        'price': price}
                return render(request, 'customer/confirm_order.html', data)
            return render(request, 'customer/order_form.html',
                          {'message': 'Please retry!', 'order_form': OrderForm(username=request.user.username),
                           'quantity_form': OrderQuantityForm()})
        return render(request, 'customer/order_form.html',
                      {
                          'order_form': OrderForm(username=request.user.username),
                          'quantity_form': OrderQuantityForm(),
                          'areas': Area.objects.all(),

                      })
    return HttpResponse(status=404)


def get_price(description, customer):
    prices = customer.discounted_price.all()
    products = string_to_list(description)
    net_price = 0
    for product in products:
        for product_price in prices:
            if product[0] == str(product_price.product.id):
                net_price += product_price.price * int(product[1])
                break
    return net_price


def get_product_quantity_map(description):
    product_list = string_to_list(description)
    print(description)
    products = Products.objects.all()
    for product_in_order in product_list:
        for product in products:
            if int(product_in_order[0]) == product.id:
                product_in_order[0] = product.name
                break
    return product_list


def has_quantity(description):
    products = string_to_list(description)
    valid = False
    for product in products:
        if int(product[1]) < 0:
            return False
        if int(product[1]) > 0:
            valid = True
    return valid


def profile(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(username=request.user.username)
        if customer:
            data = {'user': customer}
            return render(request, 'customer/profile.html', data)
    return HttpResponseNotFound()


def set_order_description(order, description):
    desc = string_to_list(description)
    products_ordered = []
    for pairs in desc:
        if int(pairs[1]) > 0:
            product = OrderDetail(product=Products.objects.get(id=pairs[0]), quantity=int(pairs[1]))
            product.save()
            products_ordered.append(product)
    order.desc.set(products_ordered)
    order.save()


def can_place_order(description, area):
    products = Products.objects.all()
    total_weight = 0
    for pairs in description:
        for product in products:
            if product.id == pairs[0]:
                total_weight += product.weight * int(pairs[1])
                break
    available_days = Schedule.objects.filter(areas=area).distinct().order_by(
        'vehicle__vehicleModel__weightCapacity').order_by('order')
    for day in available_days:
        if total_weight <= day.day_capacity:
            return True
    return False


def product_quantity_list(desc):
    product_list = []
    for products in desc:
        product_list.append([products.product.name, products.quantity])
    return product_list
