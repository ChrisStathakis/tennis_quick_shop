from django.shortcuts import render, redirect, reverse, HttpResponseRedirect

from django.contrib import messages
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse


from django_tables2 import RequestConfig
from .tables import VendorTable
from products.models import Product, ProductVendor, Category
from .models import Vendor, Note, Invoice
from .forms import VendorForm, InvoiceVendorDetailForm, EmployerForm, PaymentForm, NoteForm, VendorProductForm, Payment


@method_decorator(staff_member_required, name='dispatch')
class HomepageView(TemplateView):
    template_name = 'vendors/homepage.html'


@method_decorator(staff_member_required, name='dispatch')
class VendorListView(ListView):
    model = Vendor
    template_name = 'list_view.html'
    paginate_by = 25

    def get_queryset(self):
        qs = Vendor.objects.all()
        qs = Vendor.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_table = VendorTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(qs_table)
        queryset_table = qs_table
        create_url = reverse('vendors:create')
        page_title, back_url = 'Προμηθευτές', reverse('vendors:home')
        report_button, report_url = True, reverse('vendors:ajax_vendors_balance')
        balance_filter, search_filter = [True]*2
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateVendorView(CreateView):
    template_name = 'form_view.html'
    model = Vendor
    form_class = VendorForm

    def get_initial(self):
        initial = super().get_initial()
        # initial['site'] = 'http://'
        return initial

    def get_success_url(self):
        return self.new_object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"], context['back_url'],  = 'Δημιουργια Προμηθευτη', reverse('vendors:list')
        
        return context

    def form_valid(self, form):
        self.new_object = form.save()
        new_vendor = form.cleaned_data['title']
        messages.success(self.request, f'Ο Προμηθευτής {new_vendor} δημιουργήθηκε.')
        return super().form_valid(form)
    

@method_decorator(staff_member_required, name='dispatch')
class UpdateVendorView(UpdateView):
    model = Vendor
    template_name = 'vendors/update_vendor.html'
    form_class = VendorForm

    def get_success_url(self):
        return self.object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_form'] = InvoiceVendorDetailForm(initial={'vendor': self.object})
        context['payment_form'] = PaymentForm(initial={'vendor': self.object})
        context['employer_form'] = EmployerForm(initial={'vendor': self.object})
        context['page_title'] = f'{self.object.title}'
        context['notes'] = Note.objects.filter(vendor_related=self.object, status=True)
        context['invoices'] = Invoice.filters_data(self.request, self.object.invoices.all())
        context['payments'] = Payment.filters_data(self.request, self.object.payments.all())
        context['action_url'] = reverse('vendors:list')
        return context
    

@staff_member_required
def delete_vendor_view(request, pk):
    instance = get_object_or_404(Vendor, id=pk)
    instance.delete()
    return redirect(reverse('vendors:list'))


@method_decorator(staff_member_required, name='dispatch')
class VendorNotesView(ListView):
    template_name = 'vendors/NoteContainer.html'
    model = Note
    
    def get_queryset(self):
        self.vendor = get_object_or_404(Vendor, id=self.kwargs['pk'])
        return self.vendor.notes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Σημειώσεις {self.vendor}'
        context['back_url'] = self.vendor.get_edit_url()
        context['form'] = NoteForm(initial={'vendor_related': self.vendor})
        context['vendor'] = self.vendor
        return context


@method_decorator(staff_member_required, name='dispatch')
class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'vendors/note_update.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['vendor_related'] = self.object.vendor_related
        return initial

    def get_success_url(self):
        vendor = self.object.vendor_related
        return reverse('vendors:notes', kwargs={'pk': vendor.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = self.object.vendor_related
        context['back_url'] = self.get_success_url()
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@staff_member_required
def delete_note_view(request, pk):
    note = get_object_or_404(Note, id=pk)
    note.delete()
    return redirect(reverse('vendors:notes', kwargs={'pk': note.vendor_related.id}))


@method_decorator(staff_member_required, name='dispatch')
class VendorCardView(ListView):
    model = ProductVendor
    template_name = 'vendors/vendor_card.html'
    paginate_by = 500
    
    def get_queryset(self):
        self.vendor = vendor = get_object_or_404(Vendor, id=self.kwargs['pk'])
        qs = ProductVendor.objects.filter(vendor=vendor)
        qs = ProductVendor.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = self.vendor
        context['create_form'] = VendorProductForm(initial={'taxes_modifier': self.vendor.taxes_modifier})
        context['search_filter'], context['category_filter'] = [True] * 2
        cate_ids = self.object_list.values_list('product__categories').distinct()
        context['categories'] = Category.objects.filter(id__in=cate_ids)
        return context
