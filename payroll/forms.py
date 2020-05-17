from django import forms
from .models import Payroll, Person, Occupation
from .models import Bill,BillCategory
from .calendar_model import PersonSchedule
from .widget import XDSoftDateTimePickerInput


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PersonSheduleForm(BaseForm, forms.ModelForm):
    date_start = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=XDSoftDateTimePickerInput(attrs={'autocomplete': 'off'}), label='Απο..'
    )

    date_end = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=XDSoftDateTimePickerInput(attrs={'autocomplete': 'off'}), label='Εως...'
    )
    person = forms.ModelChoiceField(queryset=Person.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = PersonSchedule
        fields = '__all__'


class PayrollForm(BaseForm, forms.ModelForm):
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Ημερομηνια')

    class Meta:
        model = Payroll
        fields = ['is_paid', 'date_expired', 'person', 'title', 'category', 'payment_method', 'value', 'notes', ]


class PersonForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Person
        fields = ['active', 'title', 'phone', 'phone1', 'date_added', 'occupation']


class PayrollPersonForm(PayrollForm):
    person = forms.ModelChoiceField(queryset=Person.objects.all(), widget=forms.HiddenInput())


class OccupationForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Occupation
        fields = ['active', 'title', 'notes']


class CreateManyInvoicesForm(BaseForm):
    date_type = forms.ChoiceField(choices=(('a', 'days'), ('b', 'months')), required=True)
    value = forms.IntegerField(required=True, min_value=1)
    repeat = forms.IntegerField(required=True, min_value=1)

#  ------------------------------------------ bills --------------------------------------------------------------------


class BillForm(BaseForm, forms.ModelForm):
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Ημερομηνια')

    class Meta:
        model = Bill
        fields = ['is_paid', 'date_expired', 'category', 'title', 'payment_method', 'value', ]


class BillCategoryForm(BaseForm, forms.ModelForm):

    class Meta:
        model = BillCategory
        fields = ['title']


class BillFromCategoryForm(BillForm):
    category = forms.ModelChoiceField(queryset=BillCategory.objects.all(), widget=forms.HiddenInput())


class PersonBillForm(BillForm):
    person = forms.ModelChoiceField(queryset=Person.objects.all(), widget=forms.HiddenInput())

