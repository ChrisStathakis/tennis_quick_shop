from django.db.models import Sum, FloatField, F
from django.db.models.functions import TruncMonth
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django_tables2 import RequestConfig

from operator import attrgetter
from itertools import chain

from incomes.models import Income
from products.models import Product, ProductVendor
from payroll.models import Bill, Payroll
from vendors.models import Payment, Invoice, Vendor
from general_expenses.models import GeneralExpense
from .tools import sort_months


@method_decorator(staff_member_required, name='dispatch')
class AnalysisHomepage(TemplateView):
    template_name = 'analysis/homepage.html'


@method_decorator(staff_member_required, name='dispatch')
class AnalysisIncomeView(ListView):
    model = Income
    template_name = 'analysis/analysis_incomes.html'
    paginate_by = 100

    def get_queryset(self):
        qs = Income.objects.all()
        qs = Income.filters_data(self.request, qs)
        return qs

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        date_filter, currency = True, settings.CURRENCY
        back_url = reverse('analysis:homepage')
        total_z = self.object_list.aggregate(Sum('sum_z'))['sum_z__sum'] if self.object_list.exists() else 0
        total_pos = self.object_list.aggregate(Sum('pos'))['pos__sum'] if self.object_list.exists() else 0
        total_cash = total_z - total_pos
        total_order = self.object_list.aggregate(Sum('order_cost'))['order_cost__sum'] if self.object_list.exists() else 0
        total = self.object_list.aggregate(Sum('value'))['value__sum'] if self.object_list.exists() else 0
        # invoices_per_month = invoices.annotate(month=TruncMonth('date')).values('month').annotate(
        #     total=Sum('final_value')).values('month', 'total').order_by('month')
        analysis_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('logistic_value')).values('month', 'total').order_by('month')

        analysis_z_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('sum_z')).values('month', 'total').order_by('month')
        analysis_pos_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('pos')).values('month', 'total').order_by('month')
        analysis_cash_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('cash')).values('month', 'total').order_by('month')
        context.update(locals())
        return context
    

@method_decorator(staff_member_required, name='dispatch')
class AnalysisOutcomeView(TemplateView):
    template_name = 'analysis/analysis_outcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = settings.CURRENCY
        back_url = reverse('analysis:homepage')
        date_filter = True
        bills = Bill.filters_data(self.request, Bill.objects.all())
        payrolls = Payroll.filters_data(self.request, Payroll.objects.all())
        invoices = Invoice.filters_data(self.request, Invoice.objects.all())
        generic_expenses = GeneralExpense.filters_data(self.request, GeneralExpense.objects.all())
        generic_expenses_analysis = generic_expenses.values('category__title').annotate(total=Sum('value')).order_by('-total')
        generic_expenses_analysis_per_month = generic_expenses.annotate(month=TruncMonth('date')).values('month'). \
            annotate(total=Sum('value')).values('month', 'total').order_by('month')

        total_bills = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills else 0
        analysis_bills = bills.values('category__title').annotate(total=Sum('final_value')).order_by('-total')
        analysis_bills_per_month = bills.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('final_value')).values('month', 'total').order_by('month')

        total_payroll = payrolls.aggregate(Sum('final_value'))['final_value__sum'] if payrolls else 0
        total_invoices = invoices.aggregate(Sum('final_value'))['final_value__sum'] if invoices else 0
        total_generic = generic_expenses.aggregate(Sum('value'))['value__sum'] if generic_expenses else 0
        total_expenses = total_bills + total_payroll + total_invoices + total_generic
        analysis_invoices = invoices.values('vendor__title').annotate(total=Sum('final_value')).order_by('-total')
        analysis_invoices_per_month = invoices.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        payroll_analysis = payrolls.values('person__title').annotate(total=Sum('final_value')).order_by('-total')
        payroll_analysis_per_month = payrolls.annotate(month=TruncMonth('date_expired')).values('month').\
            annotate(total=Sum('final_value')).values('month', 'total').order_by('month')

        # get unique months
        months = sort_months([analysis_invoices_per_month, analysis_bills_per_month, payroll_analysis_per_month, generic_expenses_analysis_per_month])

        result_per_months = []
        for month in months:
            data = {
                'month': month,
                'total': 0
            }
            # data['invoice'] = ele['total'] for ele in analysis_invoices_per_month if ele['month'] == month else 0
            for ele in analysis_invoices_per_month:
                if ele['month'] == month:
                    data['invoice'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in analysis_bills_per_month:
                if ele['month'] == month:
                    data['bills'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in payroll_analysis_per_month:
                if ele['month'] == month:
                    data['payroll'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in generic_expenses_analysis_per_month:
                if ele['month'] == month:
                    data['generic'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            data['invoice'] = data['invoice'] if 'invoice' in data.keys() else 0
            data['bills'] = data['bills'] if 'bills' in data.keys() else 0
            data['payroll'] = data['payroll'] if 'payroll' in data.keys() else 0
            data['generic'] = data['generic'] if 'generic' in data.keys() else 0
            result_per_months.append(data)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CashRowView(TemplateView):
    template_name = 'analysis/cash_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = settings.CURRENCY
        back_url = reverse('analysis:homepage')
        incomes = Income.filters_data(self.request, Income.objects.all()).order_by('date_expired')
        total_z = incomes.aggregate(Sum('sum_z'))['sum_z__sum'] if incomes.exists() else 0
        total_pos = incomes.aggregate(Sum('pos'))['pos__sum'] if incomes.exists() else 0
        total_cash = total_z - total_pos
        total_order = incomes.aggregate(Sum('order_cost'))['order_cost__sum'] if incomes.exists() else 0
        total = incomes.aggregate(Sum('value'))['value__sum'] if incomes.exists() else 0

        date_filter = True

        # outcomes
        vendor_payments = Payment.filters_data(self.request, Payment.objects.all())
        vendor_payments_total = vendor_payments.aggregate(Sum('value'))['value__sum'] if vendor_payments.exists() else 0

        payrolls = Payroll.filters_data(self.request, Payroll.objects.filter(is_paid=True))
        payrolls_total = payrolls.aggregate(Sum('final_value'))['final_value__sum'] if payrolls.exists() else 0

        bills = Bill.filters_data(self.request, Bill.objects.filter(is_paid=True))
        bills_total = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills.exists() else 0

        generic_expenses = GeneralExpense.filters_data(self.request, GeneralExpense.objects.filter(is_paid=True))
        generic_expenses_total = generic_expenses.aggregate(Sum('value'))['value__sum'] if generic_expenses.exists() else 0

        total_expenses = vendor_payments_total + bills_total + payrolls_total + generic_expenses_total
        expenses_query = sorted(
                chain(bills, vendor_payments, payrolls, generic_expenses),
                key=attrgetter('report_date'))
        diff = round(total - total_expenses, 2)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BalanceSheetView(TemplateView):
    template_name = 'analysis/balance_sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_filter, currency = True, settings.CURRENCY

        # incomes
        incomes = Income.filters_data(self.request, Income.objects.all())
        incomes_per_month = incomes.annotate(month=TruncMonth('date_expired')).values('month').annotate(total=Sum('logistic_value')).values('month', 'total').order_by('month')
        incomes_per_month_table = incomes.annotate(month=TruncMonth('date_expired')).values('month')\
            .annotate(total_z=Sum('sum_z'),
                      total_pos=Sum('pos'),
                      total_order=Sum('order_cost'),
                      total_cash=Sum('cash'),
                      total=Sum('logistic_value')
                      ).order_by('month')
        total_z = incomes.aggregate(Sum('sum_z'))['sum_z__sum'] if incomes.exists() else 0
        total_pos = incomes.aggregate(Sum('pos'))['pos__sum'] if incomes.exists() else 0
        total_cash = total_z - total_pos
        total_order = incomes.aggregate(Sum('order_cost'))['order_cost__sum'] if incomes.exists() else 0
        incomes_total = incomes.aggregate(Sum('value'))['value__sum'] if incomes.exists() else 0

        # vendors data

        invoices = Invoice.filters_data(self.request, Invoice.objects.all())
        invoices_per_month = invoices.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        invoices_total = invoices.aggregate(Sum('final_value'))['final_value__sum'] if invoices.exists() else 0
        vendors = invoices.values('vendor__title', 'vendor__balance').annotate(total=Sum('final_value')).order_by('-total')[:15]

        # payments
        payments = Payment.filters_data(self.request, Payment.objects.all())
        payments_total = payments.aggregate(Sum('value'))['value__sum'] if payments.exists() else 0
        vendors_remaining = invoices_total - payments_total

        # bills
        bills = Bill.filters_data(self.request, Bill.objects.all())
        bills_per_month = bills.annotate(month=TruncMonth('date_expired')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        bills_total = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills.exists() else 0
        bills_paid_total = bills.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if bills.filter(is_paid=True).exists() else 0
        bills_per_bill = bills.values('category__title').annotate(total_pay=Sum('final_value'),
                                                                  paid_value=Sum('paid_value'))\
            .order_by('category__title')

        # payrolls
        payrolls = Payroll.filters_data(self.request, Payroll.objects.all())
        payroll_per_month = payrolls.annotate(month=TruncMonth('date_expired')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        payrolls_total = payrolls.aggregate(Sum('final_value'))['final_value__sum'] if payrolls.exists() else 0
        payrolls_paid_total = payrolls.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if payrolls.filter(is_paid=True).exists() else 0
        payroll_per_person = payrolls.values('person__title').annotate(total_pay=Sum('final_value'),
                                                                       paid_value=Sum('paid_value'))\
            .order_by('person__title')

        # general Expenses
        general_expenses = GeneralExpense.filters_data(self.request, GeneralExpense.objects.all())
        general_per_month = general_expenses.annotate(month=TruncMonth('date')).values('month')\
            .annotate(total=Sum('value')).values('month', 'total').order_by('month')
        general_total = general_expenses.aggregate(Sum('value'))['value__sum'] if general_expenses.exists() else 0
        general_paid = general_expenses.filter(is_paid=True)
        general_paid_total = general_paid.aggregate(Sum('value'))['value__sum'] if general_paid.exists() else 0
        expenses_per_category = general_expenses.values('category__title').annotate(total_pay=Sum('value'),
                                                                                    paid_value=Sum('paid_value'))\
            .order_by('category__title')

        # diffs
        totals = bills_total + payrolls_total + invoices_total + general_total
        paid_totals = bills_paid_total + payrolls_paid_total + payments_total + general_paid_total

        diff_paid = incomes_total - paid_totals
        diff_obligations = incomes_total - totals

        # chart analysis
        months = sort_months([incomes_per_month, invoices_per_month, payroll_per_month, bills_per_month, general_per_month])

        result_per_months = []
        for month in months:
            data = {
                'month': month,
                'total': 0
            }
            for ele in incomes_per_month:
                if ele['month'] == month:
                    data['income'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in invoices_per_month:
                if ele['month'] == month:
                    data['invoice'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in bills_per_month:
                if ele['month'] == month:
                    data['bills'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in payroll_per_month:
                if ele['month'] == month:
                    data['payroll'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in general_per_month:
                if ele['month'] == month:
                    data['generic'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            data['invoice'] = data['invoice'] if 'invoice' in data.keys() else 0
            data['bills'] = data['bills'] if 'bills' in data.keys() else 0
            data['payroll'] = data['payroll'] if 'payroll' in data.keys() else 0
            data['generic'] = data['generic'] if 'generic' in data.keys() else 0
            result_per_months.append(data)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class LogisticRowView(TemplateView):
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[""] = ''
        return context


@method_decorator(staff_member_required, name='dispatch')
class StoreInventoryView(TemplateView):
    model = Product
    template_name = 'analysis/store_inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        vendor_products = ProductVendor.objects.all()
        products_total = products.aggregate(total=Sum(F('price_buy')*F('qty'), output_field=FloatField()))\
            if products.exists() else 0
        vendor_products = vendor_products.values('taxes_modifier').annotate(total=Sum(F('product__qty')*F('product__price_buy'), output_field=FloatField())).values('taxes_modifier', 'total').order_by('taxes_modifier')
        context.update(locals())
        return context