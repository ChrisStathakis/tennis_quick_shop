from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone

from .models import Invoice, Payment, Vendor, Employer, VendorBankingAccount, Note
from products.models import Product, ProductVendor
from products.forms import ProductClassForm
from .forms import InvoiceForm, EmployerForm, VendorBankingAccountForm, PaymentForm, NoteForm, VendorProductForm, ProductVendorClassForm
from .tables import ProductVendorTable


def ajax_invoice_modal_view(request, pk):
    invoice = get_object_or_404(Invoice, id=pk)
    form = InvoiceForm(instance=invoice)
    form_title, valid_url = f'Επεξεργασια Παραστατικού { invoice }', reverse('vendors:validate_invoice_edit_view', kwargs={'pk': invoice.id})
    delete_url = reverse('vendors:action_delete_invoice', kwargs={'pk': invoice.id})
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_form.html',
                                      context=locals(),
                                      )
    return JsonResponse(data)


def ajax_payment_edit_modal_view(request, pk):
    payment = get_object_or_404(Payment, id=pk)
    form = PaymentForm(instance=payment)
    form_title, valid_url = f'Επεξεργασια πληρωμής { payment }', reverse('vendors:validate_payment_edit_view', kwargs={'pk': payment.id})
    delete_url = reverse('vendors:action_delete_payment', kwargs={'pk': payment.id})
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_form.html',
                                      context=locals(),
                                      )
    return JsonResponse(data)

def ajax_employer_edit_modal_view(request, pk):
    employer = get_object_or_404(Employer, id=pk)
    form = EmployerForm(instance=employer)
    form_title, valid_url = f'Επεξεργασία {employer.title}', reverse('vendors:validate_employer_edit_view', kwargs={'pk': employer.id})
    delete_url = reverse('vendors:action_delete_employer', kwargs={'pk': employer.id})
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_form.html',
                                      context=locals(),
                                      )
    return JsonResponse(data)


def ajax_banking_account_edit_modal_view(request, pk):
    banking_account = get_object_or_404(VendorBankingAccount, id=pk)
    form = EmployerForm(instance=banking_account)
    form_title, valid_url = f'Επεξεργασία {banking_account}', reverse('vendors:validate_employer_edit_view', kwargs={'pk': banking_account.id})
    delete_url = reverse('vendors:delete_account_banking_view', kwargs={'pk': banking_account.id})
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_form.html',
                                      context=locals(),
                                      )
    return JsonResponse(data)


def ajax_banking_account_create_modal_view(request, pk):
    vendor = get_object_or_404(Vendor, id=pk)
    form = VendorBankingAccountForm(initial={'vendor': vendor})
    form_title, valid_url = f'Δημιουργία', reverse('vendors:validate_create_banking_account', kwargs={'pk': vendor.id})
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_form.html',
                                      context=locals(),
                                      )
    return JsonResponse(data)


def ajax_banking_account_edit_modal_view(request, pk):
    banking_account = get_object_or_404(VendorBankingAccount, id=pk)
    form = VendorBankingAccountForm(instance=banking_account)
    form_title, valid_url = f'Επεξεργασια', reverse('vendors:validate_edit_banking_account', kwargs={'pk': banking_account.id})
    delete_url = reverse('vendors:delete_account_banking_view', kwargs={'pk': banking_account.id})
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_form.html',
                                      context=locals(),
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_show_product_prices(request, pk):
    instance = get_object_or_404(ProductVendor, id=pk)
    product = instance.product
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_product_price.html',
                                      context={
                                          'product': product,
                                          'instance': instance,
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_show_product_analysis_view(request, pk):
    instance = get_object_or_404(Product, id=pk)
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='vendors/ajax_views/modal_product_analysis.html',
                                      context={
                                          'instance': instance
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_search_warehouse_view(request, pk):
    vendor = get_object_or_404(Vendor, id=pk)
    search_name = request.GET.get('search_name', '')
    if len(search_name) > 2:
        qs = Product.filters_data(request, Product.objects.all())[:20]
    else: 
        qs = Product.objects.none()
    data = dict()
    data['result'] = render_to_string(template_name='vendors/ajax_views/ajax_product_container.html',
                                      request=request,
                                      context={
                                          'queryset_table': ProductVendorTable(qs),
                                          'vendor': vendor
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required 
def ajax_calculate_vendors_balance_view(request):
    vendors = Vendor.filters_data(request, Vendor.objects.all())
    total_balance = vendors.aggregate(Sum('balance'))['balance__sum'] if vendors else 0
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='ajax_views/calculate_balance_view.html',
                                      context = {
                                          'total_balance':total_balance
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_edit_product_modal(request, pk):
    instance = get_object_or_404(ProductVendor, id=pk)
    product = instance.product
    product = get_object_or_404(Product, id=product.id)
    form = ProductVendorClassForm(request.POST or None ,instance=instance)
    product_form = ProductClassForm(instance=product)
    data = dict()
    data['result'] = render_to_string(template_name='vendors/ajax_views/modal_form.html',
                                      request=request,
                                      context={
                                          'form': form,
                                          'title': f'Επεξεργασία {instance}',
                                          'product_form': product_form,
                                          'product': product,
                                          'valid_url': reverse('vendors:validate_product_vendor_edit', kwargs={'pk': instance.id}),
                                          'product_valid_url': reverse('vendors:validate_product_edit', kwargs={'pk': product.id}),
                                          'instance': instance
                                          
                                      }
                                    )
    return JsonResponse(data)


@staff_member_required
def ajax_product_modal_quick_view(request, pk):
    instance = get_object_or_404(Product, id=pk)
    data = dict()
    data['result'] = render_to_string(template_name='vendors/ajax_views/ajax_product_modal_quick_view.html',
                                      request=request,
                                      context={
                                          'instance': instance
                                      }
                                      )
    return JsonResponse(data)