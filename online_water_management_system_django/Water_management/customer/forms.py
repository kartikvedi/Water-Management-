from django import forms
from database.models import Products
from database.models import Area, Customer


class OrderQuantityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OrderQuantityForm, self).__init__(*args, **kwargs)
        products = Products.objects.all()
        for product in products:
            self.fields['%s' % product.id] = forms.IntegerField(label='%s quantity' % product.name,
                                                                  required=True, initial=0)


class OrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('username')
        super(OrderForm, self).__init__(*args, **kwargs)
        customer = Customer.objects.get(username=customer)
        area_choices = [(area, '{}'.format(area)) for area in Area.objects.all()]
        self.fields['area'] = forms.ChoiceField(choices=area_choices, widget=forms.Select(attrs={
            'class': 'selectpicker',
            'data-live-search': 'true',
        }), label="Select area to deliver order.", initial=customer.area, required=False)

    address = forms.CharField(max_length=300, label='Address (leave blank for your default address)', required=False)
    order_types = [(1, 'Once only'), (2, 'Recursive')]
    order_type = forms.ChoiceField(choices=order_types, initial=1, label='Order type')
