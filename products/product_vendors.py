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
from .tables import ProductVendorTable
from frontend.tools import build_url


@method_decorator(staff_member_required, name='dispatch')
class ProductVendorListView(ListView):
    template_name = 'products/list_view.html'
    model = ProductVendor
    paginate_by = 500

    def get_queryset(self):
        qs = ProductVendor.objects.filter(vendor__active=True)
        qs = ProductVendor.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_table = ProductVendorTable(self.object_list)
        RequestConfig(self.request, {'per_page': self.paginate_by}).configure(qs_table)
        context['queryset_table'] = qs_table
        context['vendor_filter'], context['vendors'] = True, Vendor.objects.all()
        context['search_filter'], context['favorite_filter'] = True, True
        return context