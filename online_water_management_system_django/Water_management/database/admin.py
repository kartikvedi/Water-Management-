from django.contrib import admin
from .models import Vehicle, Products, Order, Asset, CustomerAssets, Bottles, ScheduleProducts, Corporate

admin.site.register(Products)
admin.site.register(Order)
admin.site.register(Vehicle)
admin.site.register(Asset)
admin.site.register(CustomerAssets)
admin.site.register(Bottles)
admin.site.register(ScheduleProducts)
admin.site.register(Corporate)
