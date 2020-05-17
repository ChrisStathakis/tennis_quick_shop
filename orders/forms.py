from django import forms

from dal import autocomplete
from .models import Order, Payment
from costumers.models import Costumer


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class OrderMainForm(BaseForm, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'customer': autocomplete.ModelSelect2(url='orders:costumer_auto')
        }


class OrderForm(BaseForm, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    customer = forms.ModelChoiceField(Costumer.objects.all(), required=True, widget=forms.HiddenInput())

    class Meta:
        model = Order
        fields = '__all__'


class PaymentForm(BaseForm, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    customer = forms.ModelChoiceField(Costumer.objects.all(), required=True, widget=forms.HiddenInput())

    class Meta:
        model = Payment
        fields = '__all__'


class MainPaymentForm(BaseForm, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Payment
        fields = '__all__'
        widgets = {
            'customer': autocomplete.ModelSelect2(url='orders:costumer_auto')
        }