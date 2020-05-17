from django.urls import path

from .views import (
    PaymentInvoiceListView, PaymentInvoiceCreateView, PaymentInvoiceUpdateView, print_invoice_view,
                    PaymentInvoiceCreateFromOrderView, check_if_locked_view, delete_payment_invoice,
                    locked_invoice_view,
                    )
from .ajax_views import (ajax_create_item, update_costumer_detail_view, ajax_delete_order_item)
app_name = 'costumers'

urlpatterns = [
    path('home/', PaymentInvoiceListView.as_view(), name='home'),
    path('check-if-locked/', check_if_locked_view, name='check_if_locked'),
    path('payment-invoice-create/', PaymentInvoiceCreateView.as_view(), name='payment_invoice_create'),
    path('payment-invoice-create-from-costumer/<int:pk>', PaymentInvoiceCreateFromOrderView.as_view(),
         name='payment_invoice_create_costumer'),
    path('payment-update/<int:pk>/', PaymentInvoiceUpdateView.as_view(), name='payment_invoice_update'),

    path('ajax/create/<int:pk>/', ajax_create_item, name='ajax_create_item'),
    path('ajax/delete/<int:pk>/', ajax_delete_order_item, name='ajax_delete_order_item'),
    path('print/<int:pk>/', print_invoice_view, name='print_invoice'),
    path('update-invoice-profile/<int:pk>/', update_costumer_detail_view, name='update_invoice_profile'),
    path('payment-invoice-delete/<int:pk>/', delete_payment_invoice, name='delete_payment_invoice'),
    path('lnvoice/locked/<int:pk>', locked_invoice_view, name='invoice_locked')

]
