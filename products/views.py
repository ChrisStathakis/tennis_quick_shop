from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

from django_tables2.tables import RequestConfig

from .models import Product, Category, ProductVendor
from .forms import ProductFrontEndForm, ProductVendorFrontEndform
from vendors.models import Vendor
from .tables import CategoryTable, ProductTable
from frontend.tools import build_url


@method_decorator(staff_member_required, name='dispatch')
class ProductHomepageView(TemplateView):
    template_name = 'products/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['vendors'] = Vendor.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductListView(ListView):
    template_name = 'products/products_list.html'
    model = Product
    paginate_by = 50
    total_products = 0

    def get_queryset(self):
        products = Product.objects.all()
        qs = Product.filters_data(self.request, products)
        
        vendors = Vendor.filters_data(self.request, Vendor.objects.all())
        products_vendor = ProductVendor.objects.filter(vendor__in=vendors)
        qs_values = products_vendor.values_list('product__id')

        qs = qs.filter(id__in=qs_values) if qs_values else qs
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = ProductTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        context.update(locals())
        return context

    
@method_decorator(staff_member_required, name='dispatch')
class ProductEditListView(ListView):
    model = Product
    template_name = 'products/list_view.html'
    paginate_by = 50

    def get_queryset(self):
        qs = Product.objects.all()
        self.initial_data = qs
        qs = Product.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = ProductTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        context["page_title"] = 'Λιστα Προϊόντων'
        context['queryset_table'] = queryset_table
        context['back_url'] = reverse('vendors:home')
        context['create_url'] = reverse('edit_product_create')
        vendors_ids = self.initial_data.values_list('vendors')
        vendors = Vendor.objects.filter(id__in=vendors_ids)
        categories_ids = self.initial_data.values_list('categories')
        categories = Category.objects.filter(id__in=categories_ids)
        context['vendors'] = vendors
        context['categories'] = categories
        context['search_filter'], context['category_filter'], context['vendor_filter'], context['check_vendor_filter']  = [True]*4
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductFrontEndForm
    template_name = 'form_view.html'

    def get_success_url(self):
        return self.new_product.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = 'Δημιουργια Προϊόντος'
        context["back_url"] = reverse('edit_product_list')  
        return context

    def form_valid(self, form):
        self.new_product = form.save()
        return super().form_valid(form)
    

@method_decorator(staff_member_required, name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductFrontEndForm
    template_name = 'products/product_update_view.html'

    def get_success_url(self):
        return self.object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f'{self.object}'
        context['product_vendor_form'] = ProductVendorFrontEndform(initial={'product': self.object})
        context['action_url'] = reverse('edit_product_list')
        return context


@staff_member_required
def delete_product_view(request, pk):
    instance = get_object_or_404(Product, id=pk)
    instance.delete()
    messages.success(request, f'Το Προϊον {instance.title} διαγραφηκε')
    return redirect(reverse('edit_product_list'))


@staff_member_required
def copy_product_view(request, pk):
    instance = get_object_or_404(Product, id=pk)
    instance.pk = None
    instance.save()
    messages.success(request, 'Το Προιόν αντιγραφηκε επιτυχώς.')
    return redirect(instance.get_edit_url())
    

@method_decorator(staff_member_required, name='dispatch')
class ProductVendorUpdateView(UpdateView):
    model = ProductVendor
    form_class = ProductVendorFrontEndform
    template_name = 'form_view.html'

    def get_success_url(self):
        return self.object.product.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super(ProductVendorUpdateView, self).get_context_data(**kwargs)
        context['form_title'] = f'Επεξεργασια {self.object}'
        context['back_url'] = self.get_success_url()
        context['delete_url'] = self.object.get_delete_url()
        return context


@staff_member_required
def product_vendor_delete_view(request, pk):
    instance = get_object_or_404(ProductVendor, id=pk)
    instance.delete()
    messages.success(request, f'Το προϊον {instance} διαγραφηκε.')
    return redirect(instance.product.get_edit_url())


@staff_member_required
def create_product_vendor_view(request, pk):
    product = get_object_or_404(Product, id=pk)
    form = ProductVendorFrontEndform(request.POST or None, initial={'product': product})
    if form.is_valid():
        form.save()
        return redirect(product.get_edit_url())
    else:
        print(form.errors)
    return redirect(product.get_edit_url())
