from django import forms
from .models import Costumer, PaymentInvoice, CostumerDetails, InvoiceItem


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CostumerForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Costumer
        fields = ['active', 'eponimia', 'amka', 'cellphone', 'afm', 'doy',
                  'address', 'job_description', 'loading_place', 'destination',
                  'destination_city', 'transport', 'phone', 'notes'
         ]


class PaymentInvoiceForm(BaseForm, forms.ModelForm):
    # date = forms.DateTimeField(required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    #                          label='Ημερομηνια')

    class Meta:
        model = PaymentInvoice
        fields = ['date', 'order_type', 'series', 'card_info', 'costumer',
                  'payment_info', 'charges_cost', 'notes'
                  ]

    def clean_date(self):
        date = self.cleaned_data.get('date', '')
        print('date', date)
        return date


class PaymentInvoiceEditForm(PaymentInvoiceForm):
    series = forms.CharField(widget=forms.HiddenInput())
    order_type = forms.CharField(widget=forms.HiddenInput())
    costumer = forms.ModelChoiceField(queryset=Costumer.objects.all(), widget=forms.HiddenInput())


class CostumerDetailsForm(BaseForm, forms.ModelForm):
    costumer = forms.ModelChoiceField(queryset=Costumer.objects.all(), widget=forms.HiddenInput(), required=True)
    invoice = forms.ModelChoiceField(queryset=PaymentInvoice.objects.all(), widget=forms.HiddenInput(), required=True)

    class Meta:
        model = CostumerDetails
        fields = '__all__'


class CreateInvoiceItemForm(BaseForm, forms.ModelForm):
    invoice = forms.ModelChoiceField(queryset=PaymentInvoice.objects.all(), widget=forms.HiddenInput(), required=True)


    class Meta:
        model = InvoiceItem
        fields = ['title', 'unit', 'qty', 'value', 'discount',
                  'taxes_modifier', 'invoice']


