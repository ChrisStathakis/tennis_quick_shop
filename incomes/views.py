from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from .models import Income
from .tables import IncomeTable
from .forms import IncomeForm


@method_decorator(staff_member_required, name='dispatch')
class IncomeListView(ListView):
    template_name = 'incomes/list_view.html'
    model = Income
    paginate_by = 50

    def get_queryset(self):
        qs = Income.objects.all()
        qs = Income.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queryset_table'] = IncomeTable(self.object_list)
        context['create_url'] = reverse('incomes:create')
        context['date_filter'] = True
        context['search_filter'] = True
        return context


@method_decorator(staff_member_required, name='dispatch')
class InvoiceCreateView(CreateView):
    template_name = 'incomes/form_view.html'
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('incomes:list')

    def get_initial(self):
        initial = super().get_initial()
        initial['sum_z'] = 0
        initial['pos'] = 0
        initial['order_cost'] = 0
        initial['extra'] = 0
        initial['sum_z'] = 0
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        context['form_title'] = "Δημιουργια Εσοδου" 
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νεο εσοδο δημιουργηθηκε.')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class IncomeUpdateView(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'incomes/form_view.html'
    success_url = reverse_lazy('incomes:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        context['form_title'] = f'Επεξεργασια {self.object}'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'το Εσοδο Ανανεωθηκε')
        return super().form_valid(form)


@staff_member_required
def income_delete_view(request, pk):
    instance = get_object_or_404(Income, id=pk)
    instance.delete()
    messages.warning(request, 'το Εσοδο διαγραφηκε.')
    return redirect(reverse('incomes:list'))