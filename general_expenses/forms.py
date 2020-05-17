from django import forms

from .models import GeneralExpense, GeneralExpenseCategory


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class GeneralExpenseForm(BaseForm, forms.ModelForm):
    date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = GeneralExpense
        fields = ['is_paid', 'date', 'category','title', 'value', ]


class GeneralExpenseCategoryForm(BaseForm, forms.ModelForm):

    class Meta:
        model = GeneralExpenseCategory
        fields = ['title']