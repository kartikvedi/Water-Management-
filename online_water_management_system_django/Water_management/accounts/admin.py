from django.contrib import admin
from database.models import Person, Customer, City, Area, Schedule, Employee, VehicleType, CustomerPrices, OrderDetail, \
    Notifications

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

admin.site.register(Person)
admin.site.register(Customer)
admin.site.register(City)
admin.site.register(Area)
admin.site.register(Schedule)
admin.site.register(Employee)
admin.site.register(VehicleType)
admin.site.register(CustomerPrices)
admin.site.register(OrderDetail)
admin.site.register(Notifications)
