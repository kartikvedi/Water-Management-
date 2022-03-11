from django.shortcuts import render, redirect
import datetime
from customer.views import get_product_quantity_map
from database.models import Order, Customer, Area, Vehicle, Schedule, Employee, Bottles, OrderDetail, Products
from django.http import HttpResponseNotFound
from customer.views import product_quantity_list
from .forms import BottleDeliverForm, OrderDeliveryForm


def employee_schedule(request, regNo):
    if request.user.is_authenticated and request.user.is_employee:
        vehicle = Vehicle.objects.get(registrationNo=regNo)
        schedule = Schedule.objects.filter(vehicle=vehicle).order_by('order')
        data = {'schedule': schedule, "user": Employee.objects.get(username=request.user.username), 'regNo': regNo}
        return render(request, 'employee/schedule.html', data)
    return HttpResponseNotFound()


def show_schedule(request):
    if request.user.is_authenticated and request.user.is_employee:
        vehicles = Vehicle.objects.filter(employee=request.user)
        data = {'vehicles': vehicles, "user": Employee.objects.get(username=request.user.username)}
        return render(request, 'employee/selectVehicle.html', context=data)
    return HttpResponseNotFound()


def view_order(request, order_id, day=None):
    if request.user.is_authenticated and request.user.is_employee:
        order = Order.objects.get(id=order_id)
        if request.POST and "deliverButton" in request.POST:
            form = OrderDeliveryForm(request.POST)
            if form.is_valid():
                amount_received = form.cleaned_data['amount']
                bottles_received = form.cleaned_data['bottles_received']
                bottles_given = order.desc.get(product__weight=20.9).quantity
                employee = Employee.objects.get(username=request.user.username)
                if order.customer.NoOfBottles - bottles_received < 0 or bottles_received < 0:
                    messages = "Invalid No Of bottles"
                elif amount_received < 0:
                    messages = "Invalid Payment entered!"
                else:
                    if order.frequency == '1':
                        day_ = Schedule.objects.filter(orders=order).distinct().first()
                        day_.extraBottles += request.session['extraBottles']
                        request.session['extraBottles'] = None
                        day_.orders.remove(order)
                        reduce_schedule_load(order, day_)
                        product = order.desc.get(product__weight=20.9)
                        product.quantity = request.session['noOfBottles']
                        order.price = request.session['total_price']
                        product.save()
                        request.session['noOfBottles'] = None
                        request.session['total_price'] = None
                        weight = order.get_weight()
                        if day_.tolerance < day_.vehicle.vehicleModel.tolerance / 2:
                            if weight >= (day_.vehicle.vehicleModel.tolerance / 2) - day_.tolerance:
                                add_to_tolerance = (day_.vehicle.vehicleModel.tolerance / 2) - day_.tolerance
                                day_.tolerance += add_to_tolerance
                                weight -= add_to_tolerance
                                day_.day_capacity += weight
                            else:
                                day_.tolerance += weight
                        else:
                            day_.day_capacity += weight
                        day_.save()
                    bottle = Bottles.objects.all()[0]
                    bottle.filled = bottle.filled - bottles_given
                    bottle.distributed += (bottles_given - bottles_received)
                    bottle.save()
                    order.customer.NoOfBottles -= bottles_received

                    order.customer.AmountDue = order.price - amount_received + order.customer.AmountDue
                    order.delivered = True
                    order.delivered_at = datetime.datetime.now()
                    order.delivered_by = employee
                    order.customer.save()
                    order.save()

                    employee.receivedBottle += bottles_received
                    employee.receivedAmount += amount_received
                    employee.save()

                    return redirect('areawise_orders', order.vehicle.registrationNo, day, order.area.id)
                data = {'message': messages, 'Deliverform': OrderDeliveryForm(),
                        'noOfBottles': request.session['noOfBottles'], 'total_price': request.session['total_price']}
                return render(request, 'employee/order_delivery_details.html', data)
        if request.POST and "bottlesButton" in request.POST:
            form = BottleDeliverForm(request.POST)
            if form.is_valid():
                noOfBottles = form.cleaned_data['noOfBottles']
                request.session['noOfBottles'] = noOfBottles
                request.session['extraBottles'] = 0
                try:
                    quantity = order.desc.get(product__weight=20.9).quantity
                    total_price = order.price
                    request.session['total_price'] = total_price
                    if noOfBottles != quantity:
                        day_ = Schedule.objects.filter(orders=order).distinct().first()
                        if noOfBottles < quantity:
                            request.session['extraBottles'] = abs(quantity - noOfBottles)
                        elif noOfBottles > quantity + day_.extraBottles:
                            message = "No extra Bottles Available"
                            data = {'order': order, 'form': BottleDeliverForm(), 'message': message}
                            return render(request, 'employee/order_delivery_details.html', data)
                        elif noOfBottles <= (quantity + day_.extraBottles):
                            request.session['extraBottles'] = quantity - noOfBottles
                        bottle_price = order.customer.discounted_price.get(product__weight=20.9).price
                        total_price = bottle_price * noOfBottles
                        current = bottle_price * quantity
                        request.session['current'] = current
                        request.session['total_price'] = total_price
                        order.save()
                except:
                    product = OrderDetail(product=Products.objects.get(weight=20.9), quantity=noOfBottles)
                    product.save()
                    order.desc.add(product)
                    bottle_price = order.customer.discounted_price.get(product__weight=20.9).price
                    total_price = bottle_price * noOfBottles
                    order.price += total_price
                    order.save()
                order.customer.NoOfBottles += noOfBottles
                order.customer.save()
                data = {'order': order, 'Deliverform': OrderDeliveryForm(), 'noOfBottles': noOfBottles,
                        'total_price': total_price}
                if order.customer.AmountDue < 0:
                    data['credit'] = abs(order.customer.AmountDue)
                    if data['credit'] <= total_price:
                        data['amountDue'] = total_price - data['credit']
                    else:
                        data['amountDue'] = 0
                elif order.customer.AmountDue > 0:
                    data['prev_amount_due'] = order.customer.AmountDue
                    data['amountDue'] = total_price + order.customer.AmountDue
                else:
                    data['amountDue'] = total_price

            else:
                data = {'order': order, 'form': BottleDeliverForm()}
            return render(request, 'employee/order_delivery_details.html', data)

        if request.POST and request.user.is_employee and request.user.is_authenticated:
            request.session['noOfBottles'] = None
            data = {'form': BottleDeliverForm()}
            return render(request, 'employee/order_delivery_details.html', data)
        elif request.user.is_authenticated and request.user.is_employee:
            request.session['noOfBottles'] = None
            customer = order.customer
            data = {'order': order, 'quantity': product_quantity_list(order.desc.all()), 'customer': customer}
            return render(request, 'employee/ordered.html', data)

    return HttpResponseNotFound()


def areawise_orders(request, regNo, areaId, day):
    if request.user.is_authenticated and request.user.is_employee:
        vehicle = Vehicle.objects.get(registrationNo=regNo)
        area = Area.objects.get(id=areaId)
        schedule = Schedule.objects.get(vehicle=vehicle, day=day)
        regular_orders = schedule.orders.filter(frequency='2', area=area, delivered=False)
        one_time_orders = schedule.orders.filter(frequency='1', area=area, delivered=False)
        if regular_orders.first() is None and one_time_orders.first() is None:
            data = {'message': 'No orders found', 'user': Employee.objects.get(username=request.user.username)}
        else:
            data = {'regular_orders': regular_orders, 'one_time_orders': one_time_orders,
                    'user': Employee.objects.get(username=request.user.username), 'day': day}
        return render(request, 'employee/areawise_orders.html', data)
    return HttpResponseNotFound()


def delivered_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(delivered=True)
        error = None
        if not orders:
            error = 'No order found'
        context = {
            'user': Employee.objects.get(username=request.user.username),
            'orders': orders,
            'error': error,
            'massege': "Delivered orders"
        }
        if request.user.is_employee or request.user.is_superuser:
            return render(request, 'employee/order_list.html', context)
    return HttpResponseNotFound()


def not_confirmed(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(confirmed=False)
        error = None
        if not orders.first():
            error = "No order found"
        context = {
            'user': Employee.objects.get(username=request.user.username),
            'orders': orders,
            'massege': "Orders not confirmed",
            'error': error,
        }
        if request.user.is_employee or request.user.is_superuser:
            return render(request, 'employee/order_list.html', context)
    return HttpResponseNotFound()


def confirmed_not_delivered_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(delivered=False, confirmed=True)
        error = None
        if not orders:
            error = 'No order found'
        context = {
            'user': Employee.objects.get(username=request.user.username),
            'orders': orders,
            'error': error,
            'massege': 'Confirm orders'
        }
        if request.user.is_employee or request.user.is_superuser:
            return render(request, 'employee/order_list.html', context)
    return HttpResponseNotFound()


def home(request):
    if request.user.is_authenticated:
        context = {
            'user': Employee.objects.get(username=request.user.username),
            'orders': Order.objects.filter(delivered=False),
            'massege': "Orders"
        }
        if request.user.is_employee:
            return render(request, 'employee/home.html', context)
    return render(request, 'home.html')


def profile(request):
    if request.user.is_authenticated:
        data = {'user': Employee.objects.get(username=request.user.username)}
        return render(request, 'employee/profile.html', data)
    return HttpResponseNotFound()


def reduce_schedule_load(order, day):
    for product in order.desc.all():
        for load in day.daily_load.all():
            if product.product == load.product:
                load.total_quantity -= product.quantity
                load.save()
