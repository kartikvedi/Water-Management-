from django import forms


class BottleDeliverForm(forms.Form):
    noOfBottles = forms.IntegerField(initial=0, label='19 litre Bottles given')

    def clean_noOfBottles(self):
        if self.cleaned_data['noOfBottles'] < 0:
            raise ValueError("No of bottles cannot be negative")
        else:
            return self.cleaned_data['noOfBottles']


class OrderDeliveryForm(forms.Form):
    bottles_received = forms.IntegerField(initial=0, label='19 litre Bottles received')
    amount = forms.IntegerField(initial=0, label='Amount received')

    def clean_bottles_received(self):
        if self.cleaned_data['bottles_received'] < 0:
            raise ValueError("No of bottles cannot be negative")
        else:
            return self.cleaned_data['bottles_received']

    def clean_amount(self):
        if self.cleaned_data['amount'] < 0:
            raise ValueError("No of bottles cannot be negative")
        else:
            return self.cleaned_data['amount']
