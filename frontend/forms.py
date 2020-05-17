from django import forms

from .models import PaymentMethod


class BaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PaymentMethodForm(BaseForm, forms.ModelForm):

    class Meta:
        model = PaymentMethod
        fields = '__all__'
