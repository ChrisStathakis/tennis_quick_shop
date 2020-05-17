from django.urls import path
from .views import *
from .autocomplete import CostumerAutocomplete

app_name = 'orders'

urlpatterns = [
    path('list/', OrderListView.as_view(), name='home'),
    path('detail-view/<int:pk>/', OrderUpdateView.as_view(), name='order_update'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('delete/<int:pk>/', delete_order, name='order_delete'),

    path('payment/list/', PaymentListView.as_view(), name='payment_home'),
    path('payment/detail-view/<int:pk>/', PaymentUpdateView.as_view(), name='payment_update'),
    path('payment/create/', PaymentCreateView.as_view(), name='payment_create'),
    path('payment/<int:pk>/', delete_payment, name='payment_delete'),
    path('coostumer-autocomplete/', CostumerAutocomplete.as_view(), name='costumer_auto'),

    ]
