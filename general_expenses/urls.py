from django.urls import path

from .views import (GenericExpensesListView, GeneralExpenseCreateView, GeneralExpenseUpdateView, delete_generic_expense_view,
                    GenericExpensesCategoryListView, GeneralExpenseCategoryUpdateView, GeneralExpenseCategoryCreateView, delete_generic_category_expense_view,
                    pay_expense_view
                    )

app_name = 'generic_expenses'

urlpatterns = [
    path('list/', GenericExpensesListView.as_view(), name='list'),
    path('update/<int:pk>/', GeneralExpenseUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', delete_generic_expense_view, name='delete'),
    path('create/', GeneralExpenseCreateView.as_view(), name='create'),
    path('pay/<int:pk>/', pay_expense_view, name='pay_expense'),

    path('category/list/', GenericExpensesCategoryListView.as_view(), name='category_list'),
    path('category/update/<int:pk>/', GeneralExpenseCategoryUpdateView.as_view(), name='category_update'),
    path('category/delete/<int:pk>/', delete_generic_category_expense_view, name='category_delete'),
    path('category/create/', GeneralExpenseCategoryCreateView.as_view(), name='category_create'),

]
