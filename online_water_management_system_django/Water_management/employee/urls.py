from django.conf.urls import url
from .views import home, confirmed_not_delivered_orders, not_confirmed, delivered_orders, view_order, areawise_orders, \
    employee_schedule, show_schedule, profile

urlpatterns = [
    url(r'^home/$', home, name='employee_home'),
    url(r'^confirmed_not_delivered_orders/$', confirmed_not_delivered_orders, name='confirmed_not_delivered_orders'),
    url(r'^not_confirmed/$', not_confirmed, name='not_confirmed'),
    url(r'^delivered_orders/$', delivered_orders, name='delivered_orders'),
    url(r'^schedule/(?P<regNo>[ \w-]+)/(?P<day>[\w-]+)/(?P<areaId>[\w-]+)$', areawise_orders, name='areawise_orders'),
    url(r'^order/(?P<order_id>[\w-]+)/(?P<day>[\w-]+)/$', view_order, name='order_employee'),
    url(r'^order/(?P<order_id>[\w-]+)/$', view_order, name='order_employee'),
    url(r'^schedule/show/', show_schedule, name='show_employee_schedules'),
    url(r'^schedule/(?P<regNo>[ \w-]+)$', employee_schedule, name='employee_schedule'),
    url(r'^profile/$', profile, name='employee_profile'),
]
