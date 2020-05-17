from django.urls import path

from .views import (HomepageView, PayrollListView, PayrollCreateView, PayrollUpdateView, payroll_delete_view,
                    PersonListView, PersonCreateView, PersonUpdateView, person_delete_view, PersonCardView,
                    OccupationCreateView, OccupationListView, OccupationUpdateView, occupation_delete_view, 
                    PayrollCardUpdateView, payrollCard_delete_view, create_many_payroll_view, calendar_view
                    )

from .action_views import (copy_payroll_view, validate_payroll_creation_view, validate_payroll_form, copy_bill_view,
                           validate_edit_bill_form, action_pay_payroll, action_copy_payroll, action_pay_bill_view,
                           delete_schedule_view, validate_shedule_view, copy_shedule_view
                           )

from .bill_views import (BillListView, BillUpdateView, BillCreateView, bill_delete_view,
                         BillCategoryListView, BillCategoryUpdateView, BillCategoryCreateView, bill_category_delete_view,
                         BillCategoryCardView,
                         )

from .ajax_views import ajax_bill_form_modal_view

app_name = 'payroll_bills'

urlpatterns = [
    path('home/', HomepageView.as_view(), name='home'),
    path('validate/schedule/<int:pk>/', validate_shedule_view, name='validate_schedule'),
    path('calendar/<int:pk>/', calendar_view, name='person_calendar'),
    path('calendar/delete/<int:pk>/', delete_schedule_view, name='delete_schedule'),
    path('calendar/copy/<int:pk>/', copy_shedule_view, name='copy_schedule'),

    # payroll views
    path('payroll/list/', PayrollListView.as_view(), name='payroll_list'),
    path('payroll/create/', PayrollCreateView.as_view(), name='payroll_create'),
    path('payroll/update/<int:pk>/', PayrollUpdateView.as_view(), name='payroll_update'),
    path('payroll/delete/<int:pk>/', payroll_delete_view, name='payroll_delete'),
    path('action/pay-payroll/<int:pk>/', action_pay_payroll, name='action_pay_payroll'),
    path('action/payroll-copy/<int:pk>/', action_copy_payroll, name='action_copy_payroll'),
    path('action/payroll-pay/<int:pk>/', action_pay_bill_view, name='action_pay_bill'),
    path('action/payroll-create-many-payroll/', create_many_payroll_view, name='create_many_payroll'),

    path('payroll-card/update/<int:pk>/', PayrollCardUpdateView.as_view(), name='payroll_card_update'),
    path('payroll-card/delete/<int:pk>/', payrollCard_delete_view, name='payroll_card_delete'),

    # person views
    path('person/list/', PersonListView.as_view(), name='person_list'),
    path('person/create/', PersonCreateView.as_view(), name='person_create'),
    path('person/update/<int:pk>/', PersonUpdateView.as_view(), name='person_update'),
    path('person/delete/<int:pk>/', person_delete_view, name='person_delete'),
    path('person/card/<int:pk>/', PersonCardView.as_view(), name='person_card'),

    # occupation views
    path('occupation/list/', OccupationListView.as_view(), name='occupation_list'),
    path('occupation/create/', OccupationCreateView.as_view(), name='occupation_create'),
    path('occupation/update/<int:pk>/', OccupationUpdateView.as_view(), name='occupation_update'),
    path('occupation/delete/<int:pk>/', occupation_delete_view, name='occupation_delete'),

    # action
    path('action/copy-invoice/<int:pk>/', copy_payroll_view, name='copy_payroll'),
    path('action/validate-payroll/<int:pk>/', validate_payroll_creation_view, name='validate_payroll'),


    # bill-category views
    path('bill-category/list/', BillCategoryListView.as_view(), name='bill_category_list'),
    path('bill-category/create/', BillCategoryCreateView.as_view(), name='bill_category_create'),
    path('bill-category/update/<int:pk>/', BillCategoryUpdateView.as_view(), name='bill_category_update'),
    path('bill-category/delete/<int:pk>/', bill_category_delete_view, name='bill_category_delete'),
    path('bill-category-card/<int:pk>/', BillCategoryCardView.as_view(), name='bill_category_card_view'),


    path('validate-payroll/<int:pk>/', validate_payroll_form, name='validate_payroll_form'),

    # bills views
    path('bill/list/', BillListView.as_view(), name='bill_list'),
    path('bill/create/', BillCreateView.as_view(), name='bill_create'),
    path('bill/update/<int:pk>/', BillUpdateView.as_view(), name='bill_update'),
    path('bill/delete/<int:pk>/', bill_delete_view, name='bill_delete'),
    path('bill/copy/<int:pk>/', copy_bill_view, name='copy_bill_view'),
    path('action/payroll-pay/<int:pk>/', action_pay_bill_view, name='action_pay_bill'),
    path('bill/validate-edit-form/<int:pk>/', validate_edit_bill_form, name='validate_bill_edit_form'),
    

    # ajax_views

    path('ajax/show-edit-modal/<int:pk>/', ajax_bill_form_modal_view, name='ajax_edit_bill')



]
