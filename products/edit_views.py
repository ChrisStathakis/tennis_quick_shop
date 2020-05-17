from django.shortcuts import render
from django.contrib import messages
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

from django_tables2.tables import RequestConfig

from .models import Product, Category, ProductVendor
from vendors.models import Vendor
from .tables import CategoryTable, ProductTable


@method_decorator(staff_member_required, name='dispatch')
class ProductListView(ListView):
    model = Product
    template_name = ''
    



@method_decorator(staff_member_required, name='dispatch')
class ProductCreateView(CreateView):
    model = P