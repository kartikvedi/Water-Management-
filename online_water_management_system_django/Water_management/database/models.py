from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.db import models as md
from django.urls import reverse
from django.utils.timezone import now

from accounts.models import CustomerManager, UserManager, EmployeeManager


class VehicleType(md.Model):
    vehicleModel = md.CharField(max_length=255)
    weightCapacity = md.IntegerField()
    tolerance = md.IntegerField(default=0)

    def __str__(self):
        return self.vehicleModel


class City(md.Model):
    city = md.CharField(max_length=100, null=False, blank=False, unique=True)

    class Meta:
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.city


class Area(md.Model):
    city = md.ForeignKey(City, on_delete=md.CASCADE)
    name = md.CharField(max_length=100, null=False, blank=False)

    class Meta:
        unique_together = ('city', 'name',)

    def __str__(self):
        return "{}, {}".format(self.name, self.city)


class Person(AbstractBaseUser):
    username = md.CharField(max_length=30, default='', unique=True)
    email = md.CharField(verbose_name='email', max_length=100, default=' ', unique=True)
    password = md.CharField(max_length=100, )
    name = md.CharField(max_length=30, default=' ')
    PhoneNo = md.CharField(max_length=11, null=True, blank=True)
    cnic = md.CharField(max_length=13, null=True, blank=True)
    is_active = md.BooleanField(default=True)
    is_available = md.BooleanField(default=True)
    is_admin = md.BooleanField(default=False)
    is_staff = md.BooleanField(default=False)
    is_approved = md.BooleanField(default=False)
    is_customer = md.BooleanField(default=False)
    is_corporate = md.BooleanField(default=False)
    is_employee = md.BooleanField(default=False)
    created_at = md.DateTimeField(auto_now_add=True)
    updated_at = md.DateTimeField(auto_now=True)
    area = md.ForeignKey(Area, on_delete=md.CASCADE, null=True, blank=True)
    address = md.CharField(max_length=120, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'email']
    objects = UserManager()

    def get_url(self):
        return reverse('details', kwargs={'username': self.username})

    def get_url_customer(self):
        return reverse('customer_profile', kwargs={'username': self.username})

    def get_url_employee(self):
        return reverse('employee_profile', kwargs={'username': self.username})

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self._is_staff = value

    def __str__(self):
        return self.name + '---------' + self.username


class Employee(Person):
    receivedAmount = md.IntegerField(default=0, null=False, blank=False)
    receivedBottle = md.IntegerField(default=0)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']
    objects = EmployeeManager()


class Customer(Person):
    NoOfBottles = md.IntegerField(default=0, null=True, blank=True)
    AmountDue = md.IntegerField(default=0, null=True, blank=True)
    MonthlyBill = md.IntegerField(default=0, null=True, blank=True)
    discounted_price = md.ManyToManyField('CustomerPrices')
    assets = md.ManyToManyField('CustomerAssets', null=True, blank=True)
    AverageWeekly = md.IntegerField(null=True, blank=True)
    NotInArea = md.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']
    objects = CustomerManager()


class CustomerPrices(md.Model):
    product = md.ForeignKey('Products', on_delete=md.CASCADE)
    price = md.IntegerField(default=0)

    class Meta:
        verbose_name = 'Customer Assigned Price'

    def __str__(self):
        return "%s -- %s" % (self.product.name, self.price)


class Vehicle(md.Model):
    registrationNo = md.CharField(max_length=15, blank=False, null=False, unique=True)
    employee = md.ForeignKey(Employee, on_delete=md.SET_NULL, null=True, blank=True)
    vehicleModel = md.ForeignKey(VehicleType, on_delete=md.SET_NULL, null=True)

    def __str__(self):
        return self.registrationNo


class Products(md.Model):
    name = md.CharField(max_length=80, null=False, blank=False)
    price = md.IntegerField(null=False, blank=False)
    description = md.CharField(max_length=500, blank=True, null=True)
    weight = md.FloatField(default=0)

    class Meta:
        verbose_name = "Product"

    def __str__(self):
        return self.name


class Order(md.Model):
    frequencyChoices = [('1', "One Time"), ('2', "Recursive")]
    priority_choices = [(1, 'Normal'), (2, 'High')]
    delivered = md.BooleanField(default=False)
    customer = md.ForeignKey(Customer, on_delete=md.CASCADE,
                             limit_choices_to={'is_customer': True}, related_name='%(class)s_is_customer')
    address = md.CharField(max_length=120, null=True, blank=True)
    desc = md.ManyToManyField("OrderDetail")  # 'a1:0, a2:0' this is formate for system
    frequency = md.CharField(max_length=1, choices=frequencyChoices, default=frequencyChoices[0], blank=False,
                             null=False)
    ordered_at = md.DateTimeField(default=now)
    delivered_at = md.DateTimeField(null=True, blank=True, default=None)
    price = md.IntegerField(default=0)
    area = md.ForeignKey('Area', null=True, blank=True, on_delete=md.SET_NULL)
    confirmed = md.BooleanField(default=False)
    vehicle = md.ForeignKey(Vehicle, on_delete=md.SET_NULL, null=True)
    delivered_by = md.ForeignKey(Employee, on_delete=md.SET_NULL, null=True)
    priority = md.IntegerField(choices=priority_choices, default=1)

    def get_url(self):
        return reverse('order', kwargs={'order_id': self.id})

    def get_url_employee(self):
        return reverse('order_employee', kwargs={'order_id': self.id})

    def get_url_customer(self):
        return reverse('order_customer', kwargs={'order_id': self.id})

    def get_weight(self):
        weight = 0
        for selected_product in self.desc.all():
            weight += selected_product.product.weight * selected_product.quantity
        return weight

    def delete(self, using=None, keep_parents=False):
        desc = self.desc.all()
        for item in desc:
            item.delete()
            print('deleting')
        return self.delete(using=using, keep_parents=keep_parents)


class OrderDetail(md.Model):
    product = md.ForeignKey(Products, on_delete=md.CASCADE)
    quantity = md.IntegerField(default=0)

    def __str__(self):
        return '%s -- %d' % (self.product.name, self.quantity)


class Schedule(md.Model):
    day_choices = [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                   ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')]
    vehicle = md.ForeignKey(Vehicle, on_delete=md.CASCADE, null=True)
    day = md.CharField(max_length=10, null=False, blank=False, choices=day_choices)
    areas = md.ManyToManyField(Area, null=True, blank=True)
    order = md.IntegerField(null=False, default=0, blank=False, editable=False)
    day_capacity = md.FloatField(default=0)
    tolerance = md.FloatField(default=0)
    orders = md.ManyToManyField(Order, null=True, blank=True)
    extraBottles = md.IntegerField(default=0)
    daily_load = md.ManyToManyField('ScheduleProducts')

    def __str__(self):
        return "%s -- %s" % (self.day, self.vehicle)

    def extraProductSpace(self, weight):
        return round(self.day_capacity / weight)


class ScheduleProducts(md.Model):
    product = md.ForeignKey(Products, on_delete=md.CASCADE)
    total_quantity = md.IntegerField(default=0)

    class Meta:
        verbose_name = 'Schedule Product'

    def __str__(self):
        return '%s -- %d' % (self.product, self.total_quantity)


class Asset(md.Model):
    name = md.CharField(max_length=50)
    total_amount = md.IntegerField()
    distributed = md.IntegerField(default=0)
    desc = md.TextField(null=True, blank=True)

    def get_remaining(self):
        return self.total_amount - self.distributed

    def __str__(self):
        return self.name


class Notifications(md.Model):
    description = md.CharField(max_length=255)
    order = md.ForeignKey(Order, on_delete=md.CASCADE, null=True, unique=True)

    class Meta:
        verbose_name = "Notification"

    def __str__(self):
        return self.description


class Corporate(Customer):
    NTN = md.IntegerField(null=True, blank=True)
    STRN = md.IntegerField(null=True, blank=True)
    registration_number = md.IntegerField(null=True, blank=True)
    registered_address = md.CharField(max_length=100, null=True, blank=True)


class CustomerAssets(md.Model):
    asset = md.ForeignKey(Asset, on_delete=md.CASCADE)
    amount = md.IntegerField(default=0)

    def __str__(self):
        return "%s ---- %d" % (self.asset.name, self.amount)

    class Meta:
        verbose_name = "Customer Asset"


class Bottles(md.Model):
    name = md.CharField(max_length=50, default='19 Litre Bottle')
    total = md.IntegerField()
    filled = md.IntegerField()
    distributed = md.IntegerField()
