from django import forms
from tinymce.widgets import TinyMCE

from dal import autocomplete

from .models import Vendor, Invoice, Payment, Vendor, Employer, VendorBankingAccount, Note, TAXES_CHOICES
from products.models import Category
from products.models import Product, ProductVendor


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class VendorForm(BaseForm, forms.ModelForm):
    site = forms.URLField(widget=forms.TextInput(), required=False)

    class Meta:
        model = Vendor
        fields = ['active', 'title', 'owner', 'afm', 'doy', 'phone', 'cellphone', 'address', 'email', 'site', 'taxes_modifier']

    def clean_site(self):
        data = self.cleaned_data.get('site', None)
        if data:
            if not 'http' in data:
                data = 'https://'+ data
        return data


class InvoiceVendorDetailForm(BaseForm, forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label='Ημερομηνία')

    class Meta:
        model = Invoice
        fields = ['date', 'title', 'vendor', 'value', 'extra_value', 'payment_method', 'description']


class InvoiceForm(BaseForm, forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label='Ημερομηνία')

    class Meta:
        model = Invoice
        fields = '__all__'


class PaymentForm(BaseForm, forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    
    class Meta:
        model = Payment
        fields = '__all__'


class EmployerForm(BaseForm, forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Employer
        fields = '__all__'


class VendorBankingAccountForm(BaseForm, forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())
    
    class Meta:
        model = VendorBankingAccount
        fields = '__all__'


class NoteForm(BaseForm, forms.ModelForm):
    vendor_related = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())
    text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 200}))
    
    class Meta:
        model = Note
        fields = ['status', 'title', 'text', 'vendor_related']


class VendorProductForm(BaseForm, forms.ModelForm):
    warehouse_value = forms.DecimalField(required=True, label='Αξια Τιμολογιου')
    discount = forms.IntegerField(required=True, label='Εκπτωση Τιμολογιου')
    extra_value = forms.DecimalField(required=True, label='Επιπλεον Αξια')
    taxes_modifier = forms.ChoiceField(choices=TAXES_CHOICES, label='ΦΠΑ')
    is_favorite = forms.BooleanField(label='Αγαπημένο', required=False)
    sku_ware = forms.CharField(label='Κωδικός Τιμολογίου', required=False)
    
    class Meta:
        model = Product
        fields = ['active', 'is_favorite', 'title', 'sku', 'categories',
                  'sku_ware',
                  'warehouse_value', 'discount', 'extra_value',  
                  'qty', 'value', 'taxes_modifier', 
                  
        ]


class ProductVendorClassForm(BaseForm, forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = ProductVendor
        fields = ['is_favorite', 'product', 'vendor', 'sku', 'value',
                  'discount', 'added_value', 'taxes_modifier'
        ]
        

class CopyProductToNewVendor(BaseForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), label='Προμηθευτής')
    value = forms.DecimalField(required=True)
    discount = forms.IntegerField(required=True)
    added_value = forms.DecimalField(required=True)


class CopyProductFromVendorCardForm(BaseForm, forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), widget=forms.HiddenInput())
    class Meta:
        model = ProductVendor
        fields = ['product', 'vendor', 'sku', 'value', 'discount', 'added_value','taxes_modifier']

    

