from django import forms

from .models import Income
from vendors.forms import BaseForm

class IncomeForm(BaseForm, forms.ModelForm):
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Ημερομηνια')
    
    class Meta:
        model = Income
        fields = ['date_expired', 'sum_z' ,'pos', 'order_cost', 'extra', 'notes']