from django.conf.urls import url
from .views import order, my_orders, view_order, order_confirmed, home, profile

urlpatterns = [
    url(r'^home/$', home, name='customer_home'),
    url(r'^all-orders/$', my_orders, name="all_orders_customer"),
    url(r'^order-confirmed/$', order_confirmed, name='order_confirm_customer'),
    url(r'^order/$', order),
    url(r'^order/(?P<order_id>[\w-]+)/$', view_order, name='order_customer'),
    url(r'^profile/$', profile, name='customer_profile'),
]
