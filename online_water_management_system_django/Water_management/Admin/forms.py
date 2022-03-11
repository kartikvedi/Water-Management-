from django import forms
from database.models import Person, City, Area, Vehicle, Schedule, Customer, Order, Products, Employee


class EmployeeCreateForm(forms.ModelForm):
    confirmPassword = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = Employee
        fields = ['name', 'username', 'email', 'cnic', 'password', 'confirmPassword', 'PhoneNo', 'address']
        labels = {'name': 'Name', 'username': 'Username', 'email': 'Email', 'cnic': 'CNIC', 'password': 'Password',
                  'confirmPassword': "Re-enter Password", 'PhoneNo': "Phone number", 'address': 'Address'}
        widgets = {
            'password': forms.PasswordInput
        }

    def clean_confirmPassword(self):
        password = self.cleaned_data.get('password')
        confirmPassword = self.cleaned_data.get('confirmPassword')
        if password == confirmPassword:
            return confirmPassword
        return ValueError("Passwords Do not Match")

    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.set_password(self.cleaned_data['password'])
        employee.is_employee = True
        employee.is_approved = True
        employee.is_available = True
        employee.save()
        return employee


class CityCreateForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['city']
        labels = {'city': "City"}


class AreaCreateForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['city', 'name']
        labels = {"city": "City", "name": "Name"}


class VehicleCreateForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['registrationNo', 'vehicleModel', 'employee']
        labels = {"registrationNo": "Registration Number", "employee": "Employee", 'vehicleModel': 'Model'}


class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'cnic', 'PhoneNo', 'MonthlyBill', 'NoOfBottles',
                  'AmountDue']
        labels = {'name': 'Name', 'email': 'Email', 'cinc': 'CNIC', 'PhoneNo': 'Phone No',
                  'MonthlyBill': 'Monthly Bill', 'AmountDue': 'Amount Due'}


class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'email', 'cnic', 'PhoneNo', 'address']
        labels = {'name': 'Name', 'email': 'Email', 'cnic': 'CNIC', 'PhoneNo': "Phone number", 'address': 'Address'}
        widgets = {
            'address': forms.Textarea
        }


class VehicleEditForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['employee']
        labels = {'employee': "Employee"}


class SearchOrdersForm(forms.Form):
    options = [('all', 'all'), ('delivered', 'delivered'), ('confirmed', 'confirmed'), ('unconfirmed', 'unconfirmed'),
               ('regular', 'regular'), ('only once', 'only once'),
               ("confirmed & not delivered", "confirmed & not delivered")]
    status = forms.CharField(label="Status", max_length=30, widget=forms.Select(choices=options))
    customer_search = forms.CharField(label="Customer Name or Order id", max_length=255, required=False)


class PersonSearchForm(forms.Form):
    name = forms.CharField(label="Name or id", max_length=255, required=False)


class VehicleSearchForm(forms.Form):
    regNo = forms.CharField(label="Reg No.", max_length=255, required=False)


class ConfirmOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['priority']
        labels = {'priority': 'Priority'}

    def save(self, commit=True):
        order = super().save(commit=False)
        order.confirmed = True
        order.save()
        return order


# currently below form is useless
class SelectAreaOfOrderForm(forms.Form):
    area_name = ""
    city_name = ""

    def __init__(self, *args, **kwargs):
        self.area_name = kwargs.pop('area')
        super(SelectAreaOfOrderForm, self).__init__(*args, **kwargs)
        self.area_name, self.city_name = str(self.area_name).split(',')
        print(self.area_name)
        self.vehicle_schedule = []
        self.schedule = Schedule.objects.all()
        for day in self.schedule:
            for area in day.areas.all():
                if area.name == self.area_name:
                    self.vehicle_schedule.append(day)
                    break
        self.choices = [("{}".format(day.vehicle.registrationNo), "{}, {}".format(day.vehicle.registrationNo, day.day))
                        for day in self.vehicle_schedule]
        self.fields['vehicle'] = forms.CharField(label='Delivery Vehicle', max_length=255,
                                                 widget=forms.Select(choices=self.choices, attrs={
                                                     'class': 'selectpicker',
                                                     'data-live-search': 'true',
                                                 }))


class AddDiscountedPrices(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AddDiscountedPrices, self).__init__(*args, **kwargs)
        products = Products.objects.all()
        for product in products:
            self.fields['%s' % product.id] = forms.IntegerField(label='%s price' % product.name,
                                                                required=True, initial=product.price)


class CustomerApprovalForm(forms.Form):
    approve_list = [("1", 'Not approved'), ("2", 'Approve'), ('3', 'Block')]

    NoOfBottles = forms.IntegerField(label='Number Of Bottles', min_value=0)
    MonthlyBill = forms.IntegerField(label='Mothly Bill', min_value=0)
    status = forms.ChoiceField(label='Status', choices=approve_list, initial=1)


class CreateProductForm(forms.ModelForm):
    liquid = forms.FloatField(label="Liquid Quantity in litres")
    quantity_in_a_pack = forms.IntegerField(label="No. of products in a carton")

    class Meta:
        model = Products
        fields = ['name', 'liquid', 'quantity_in_a_pack', 'price', 'description']
        labels = {'name': 'Name', 'price': 'Price', 'description': 'Description'}
        widgets = {'description': forms.Textarea()}


class EditProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'price', 'description']
        labels = {'name': 'Name', 'price': 'Price', 'description': 'Description'}
        widgets = {'description': forms.Textarea()}


class AddExtraBottlesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.max = kwargs.pop('max')
        super(AddExtraBottlesForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Schedule
        fields = ['extraBottles']
        labels = {'extraBottles': ''}

    def clean_extraBottles(self):
        bottles = self.cleaned_data['extraBottles']
        if bottles < 0 or bottles > self.max:
            return 0
        else:
            return bottles
