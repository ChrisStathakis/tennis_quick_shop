from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from .models import GeneralExpenseCategory, GeneralExpense
from .tables import GeneralExpenseTable, GeneralExpenseCategoryTable
from .forms import GeneralExpenseForm, GeneralExpenseCategoryForm
from django_tables2 import RequestConfig


@method_decorator(staff_member_required, name='dispatch')
class GenericExpensesListView(ListView):
    template_name = 'general_expenses/list_view.html'
    model = GeneralExpense
    paginate_by = 50

    def get_queryset(self):
        qs = GeneralExpense.objects.all()
        qs = GeneralExpense.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse('payroll_bills:home')
        context['create_url'] = reverse('generic_expenses:create')
        qs_table = GeneralExpenseTable(self.object_list)
        RequestConfig(self.request, {'per_page': self.paginate_by}).configure(qs_table)
        context['queryset_table'] = qs_table
        context['date_filter'], context['search_filter'], context['category_filter'] = [True] * 3
        categories = GeneralExpenseCategory.objects.all()
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class GeneralExpenseCreateView(CreateView):
    model = GeneralExpense
    form_class = GeneralExpenseForm
    template_name = 'general_expenses/form_view.html'
    success_url = reverse_lazy('generic_expenses:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['form_title'] = 'Δημιουργια Εξοδου'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Το εξοδο δημιουργηθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class GeneralExpenseUpdateView(UpdateView):
    model = GeneralExpense
    form_class = GeneralExpenseForm
    success_url = reverse_lazy('generic_expenses:list')
    template_name = 'general_expenses/form_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['form_title'] = 'Δημιουργια Εξοδου'
        context['delete_url'] = self.object.get_delete_url()
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Το εξοδο επεξερεγαστηκε')
        return super().form_valid(form)


@staff_member_required
def delete_generic_expense_view(request, pk):
    instance = get_object_or_404(GeneralExpense, id=pk)
    instance.delete()
    messages.success(request, 'Το εξοδο διαγραφηκε')
    return redirect(reverse('generic_expenses:list'))


@method_decorator(staff_member_required, name='dispatch')
class GenericExpensesCategoryListView(ListView):
    template_name = 'general_expenses/list_view.html'
    model = GeneralExpenseCategory
    paginate_by = 50

    def get_queryset(self):
        qs = GeneralExpenseCategory.objects.all()
        qs = GeneralExpenseCategory.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse('payroll_bills:home')
        context['create_url'] = reverse('generic_expenses:category_create')
        qs_table = GeneralExpenseCategoryTable(self.object_list)
        RequestConfig(self.request, {'per_page': self.paginate_by}).configure(qs_table)
        context['queryset_table'] = qs_table
        context['search_filter'] = [True]
        return context


@method_decorator(staff_member_required, name='dispatch')
class GeneralExpenseCategoryCreateView(CreateView):
    model = GeneralExpenseCategory
    form_class = GeneralExpenseCategoryForm
    template_name = 'general_expenses/form_view.html'
    success_url = reverse_lazy('generic_expenses:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['form_title'] = 'Δημιουργια Κατηγοριας'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η Κατηγορια δημιουργηθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class GeneralExpenseCategoryUpdateView(UpdateView):
    model = GeneralExpenseCategory
    form_class = GeneralExpenseCategoryForm
    template_name = 'general_expenses/form_view.html'
    success_url = reverse_lazy('generic_expenses:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['form_title'] = 'Δημιουργια Εξοδου'
        context['delete_url'] = self.object.get_delete_url()
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η Κατηγορια επεξεργαστηκε')
        return super().form_valid(form)


@staff_member_required
def delete_generic_category_expense_view(request, pk):
    instance = get_object_or_404(GeneralExpenseCategory, id=pk)
    instance.delete()
    messages.success(request, 'Το εξοδο διαγραφηκε')
    return redirect(reverse('generic_expenses:category_list'))


@staff_member_required
def pay_expense_view(request, pk):
    instance = get_object_or_404(GeneralExpense, id=pk)
    instance.is_paid = False if instance.is_paid else True
    instance.save()
    return redirect(reverse('generic_expenses:list'))