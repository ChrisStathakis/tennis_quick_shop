from django.shortcuts import reverse, redirect, render, get_object_or_404
from django.views.generic import ListView, UpdateView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required


from .models import Bill, BillCategory, Payroll
from .forms import BillForm, BillCategoryForm, BillFromCategoryForm
from .tables import BillCategoryTable, BillTable, BillFromCategoryTable


@method_decorator(staff_member_required, name='dispatch')
class BillListView(ListView):
    model = Bill
    template_name = 'payroll/list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = Bill.objects.all()
        qs = Bill.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Λογαριασμοι'
        context['back_url'] = reverse('payroll_bills:home')
        context['create_url'] = reverse('payroll_bills:bill_create')
        context['bills'] = True
        context['queryset_table'] = BillTable(self.object_list)
        context['search_filter'], context['date_filter'] = [True]*2
        context['paid_filter'] = True
        context['category_filter'] = True

        context['categories'] = BillCategory.objects.filter(active=True)
        return context
    
    
@method_decorator(staff_member_required, name='dispatch')
class BillCreateView(CreateView):
    model = Bill
    template_name = 'payroll/form.html'
    form_class = BillForm
    success_url = reverse_lazy('payroll_bills:bill_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Δημιουργια Πληρωμής'
        context['back_url'] = self.success_url
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νεος Λογαριασμος Δημιουργηθηκε')
        return super().form_valid(form)
    
    
@method_decorator(staff_member_required, name='dispatch')
class BillUpdateView(UpdateView):
    model = Bill
    template_name = 'payroll/form.html'
    form_class = BillForm
    success_url = reverse_lazy('payroll_bills:bill_list')
    
    def get_context_data(self, **kwargs):
        context = super(BillUpdateView, self).get_context_data(**kwargs)
        context['form_title'] = f'Επεξεργασια {self.object}'
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f'Η πληρωμη {self.object} πραγματοποιηθηκε')
        return super(BillUpdateView, self).form_valid(form)


@staff_member_required
def bill_delete_view(request, pk):
    instance = get_object_or_404(Bill, id=pk)
    instance.delete()
    messages.warning(request, 'Το Παραστατικο Διαγραφηκε.')
    return redirect(reverse('payroll_bills:bill_list'))


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryListView(ListView):
    template_name = 'payroll/list.html'
    model = BillCategory
    paginate_by = 50

    def get_queryset(self):
        qs = BillCategory.objects.all()
        qs = BillCategory.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Κατηγορια Λογαριασμων'
        context['back_url'] = reverse('payroll_bills:home')
        context['create_url'] = reverse('payroll_bills:bill_category_create')
        context['queryset_table'] = BillCategoryTable(self.object_list)
        return context


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryUpdateView(UpdateView):
    model = BillCategory
    form_class = BillCategoryForm
    success_url = reverse_lazy('payroll_bills:bill_category_list')
    template_name = 'payroll/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        context['form_title'] = f'Επεξεργασια {self.object}'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f'Ο Λογαριασμος δημιουργήθηκε.')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryCreateView(CreateView):
    model = BillCategory
    form_class = BillCategoryForm
    success_url = reverse_lazy('payroll_bills:bill_category_list')
    template_name = 'payroll/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Δημιουργια Λογαριασμού'
        context['back_url'] = reverse('payroll_bills:bill_category_list')
        return context

    def form_valid(self, form):
        form.save()
        bill = form.cleaned_data.get('title', 'No data')
        messages.success(self.request, f'Ο Λογαριασμός {bill} επεξεργαστηκε.')
        return super(BillCategoryCreateView, self).form_valid(form)


@staff_member_required
def bill_category_delete_view(request, pk):
    instance = get_object_or_404(BillCategory, id=pk)
    instance.delete()
    messages.warning(request, f'Ο Λογαριασμός {instance} διαγράφηκε.')
    return redirect(reverse('payroll_bills:bill_category_list'))


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryCardView(ListView):
    model = Bill
    template_name = 'payroll/bill_card.html'
    paginate_by = 30

    def get_queryset(self):
        self.category = get_object_or_404(BillCategory, id=self.kwargs['pk'])
        qs = Bill.objects.filter(category=self.category)
        qs = Bill.filters_data(self.request, qs)

        return qs

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['form'] = BillFromCategoryForm(initial={'category': self.category, 'is_paid': True})
        context['category'] = self.category
        context['page_title'] = self.category.title + '. Υπολοιπο ==> ' + self.category.tag_balance()
        context['queryset_table'] = BillFromCategoryTable(self.object_list)
        return context


