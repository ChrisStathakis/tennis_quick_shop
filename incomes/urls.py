from django.urls import path, include
from .views import IncomeListView, InvoiceCreateView, IncomeUpdateView, income_delete_view

app_name = 'incomes'

urlpatterns = [
    path('list/', IncomeListView.as_view(), name='list'),
    path('create/', InvoiceCreateView.as_view(), name='create'),
    path('update/<int:pk>/', IncomeUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', income_delete_view, name='delete'),
   
]
