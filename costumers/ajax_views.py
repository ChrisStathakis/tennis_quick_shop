from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template.loader import render_to_string
from django.http import JsonResponse

from .models import PaymentInvoice, InvoiceItem, CostumerDetails
from .forms import CreateInvoiceItemForm, CostumerDetailsForm


@staff_member_required
def ajax_create_item(request, pk):
    instance = get_object_or_404(PaymentInvoice, id=pk)
    form = CreateInvoiceItemForm(request.POST or None, initial={'invoice': instance})
    if form.is_valid():
        form.save()
    instance.refresh_from_db()
    data = dict()
    data['result'] = render_to_string(template_name='costumers/ajax/order_items.html',
                                      request=request,
                                      context={'object': instance})
    data['details'] = render_to_string(template_name='costumers/ajax/order_details.html',
                                       request=request,
                                       context={
                                           'object': instance
                                       }
                                       )
    return JsonResponse(data)


@staff_member_required
def ajax_delete_order_item(request, pk):
    instance = get_object_or_404(InvoiceItem, id=pk)
    order = instance.invoice
    instance.delete()
    order.refresh_from_db()
    data = dict()
    data['result'] = render_to_string(template_name='costumers/ajax/order_items.html',
                                      request=request,
                                      context={
                                          'object': order
                                      }
                                      )
    data['details'] = render_to_string(template_name='costumers/ajax/order_details.html',
                                       request=request,
                                       context={
                                           'object': order
                                       }
                                       )
    return JsonResponse(data)

@staff_member_required
def update_costumer_detail_view(request, pk):
    instance = get_object_or_404(CostumerDetails, id=pk)
    form = CostumerDetailsForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
    else:
        print(form.errors)
    return redirect(instance.invoice.get_edit_url())


