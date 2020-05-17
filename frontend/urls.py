from django.urls import path, include
from .views import (HomepageView, CostumerListView, CreateOrderFromCostumerView,
                    CreatePaymentFromCostumerView, CostumerDetailView, CostumerCreateView,
                    delete_costumer_view, empty_costumer_log_view, CreateOrderFromCostumerDetailView,
                    CreatePaymentFromCostumerDetailView, EditOrderFromCostumerView, delete_order_from_costumer,
                    EditPaymentFromCostumerView, delete_payment_from_costumer, analysis_view, logout_view, PrintListView,
                    CostumerHomepageView
                    )
from .ajax_views import (quick_view_costumer_view, quick_pay_costumer_view, ajax_calculate_balance, ajax_analysis_view,
                         ajax_quick_order_view, ajax_quick_payment_view, create_costumer_invoice_view)

from .settings_view import PaymentMethodListView, PaymentMethodUpdateView, PaymentMethodCreateView, payment_method_delete_view


urlpatterns = [
    path('', HomepageView.as_view(), name='home'),
    path('costumers/', CostumerListView.as_view(), name='costumer_list'),
    path('costumer-homepage/', CostumerHomepageView.as_view(), name='costumer_homepage'),
    path('costumers/create/', CostumerCreateView.as_view(), name='costumers_create'),
    path('costumer/detail-view/<int:pk>/', CostumerDetailView.as_view(), name='costumer_detail_view'),
    path('costumer/create/order/<int:pk>/', CreateOrderFromCostumerView.as_view(), name='create_order_costumer_view'),
    path('costumer/create/detail/payment/<int:pk>/', CreatePaymentFromCostumerView.as_view(), name='create_payment_costumer_view'),
    path('costumer/create/detail/order/<int:pk>/', CreateOrderFromCostumerDetailView.as_view(), name='create_order_costumer_detail'),
    path('costumer/create/payment/<int:pk>/', CreatePaymentFromCostumerDetailView.as_view(),
         name='create_payment_costumer_detail'),
    path('costumer/detail/<int:pk>/', CostumerDetailView.as_view(), name='costumer_detail'),

    path('costumer/delete/<int:pk>/', delete_costumer_view, name='costumer_delete'),
    path('costumer/empty/log/<int:pk>/', empty_costumer_log_view, name='costumer_empty_log'),
    path('logout/', logout_view, name='logout'),

    path('costumer/order/edit/<int:pk>/', EditOrderFromCostumerView.as_view(), name='edit_order_from_costumer'),
    path('costumer/order/delete/<int:pk>/', delete_order_from_costumer, name='delete_order_from_costumer'),

    path('payment/order/edit/<int:pk>/', EditPaymentFromCostumerView.as_view(), name='edit_payment_from_costumer'),
    path('payment/order/delete/<int:pk>/', delete_payment_from_costumer, name='delete_payment_from_costumer'),

    path('analysis/', analysis_view, name='analysis'),

    path('orders/', include('orders.urls')),


    # ajax
    path('costumer/quick_view/<int:pk>/', quick_view_costumer_view, name='costumer_quick_view'),
    path('costumer/quick-pay/<int:pk>/', quick_pay_costumer_view, name='costumer_quick_pay'),
    path('ajax/costumer-calculate-balance/', ajax_calculate_balance, name='ajax_calculate_balance'),
    path('ajax/analysis/costumers/', ajax_analysis_view, name='ajax_analysis_view'),
    path('ajax/order-quick-view/<int:pk>/', ajax_quick_order_view, name='ajax_quick_order_view'),
    path('ajax/payment-quick-view/<int:pk>/', ajax_quick_payment_view, name='ajax_quick_payment_view'),

    path('print-costumers/', PrintListView.as_view(), name='print_list'),
    path('create-invoice-from-order/<int:pk>/', create_costumer_invoice_view, name='create_costu_inv_from_order'),

    path('payment-method/list/', PaymentMethodListView.as_view(), name='payment_method_list'),
    path('payment-method/create/', PaymentMethodCreateView.as_view(), name='payment_method_create'),
    path('payment-method/update/<int:pk>/', PaymentMethodUpdateView.as_view(), name='payment_method_update'),
    path('payment-method/delete/<int:pk>/', payment_method_delete_view, name='payment_method_delete')


    ]
