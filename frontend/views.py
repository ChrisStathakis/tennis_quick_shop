from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth import logout
from django.db.models import Sum
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta

from costumers.models import Costumer
from .tables import CostumerTable
from .mixins import MyFormMixin

from orders.models import Order, Payment
from orders.forms import OrderForm, PaymentForm
from orders.tables import OrderTable, PaymentTable
from costumers.forms import CostumerForm
from incomes.models import Income
from payroll.models import Bill, Payroll
from vendors.models import Vendor, Invoice

CURRENCY = settings.CURRENCY


@method_decorator(staff_member_required, name='dispatch')
class HomepageView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = CURRENCY
        date_start, date_end = datetime.today().replace(day=1), datetime.today()
        incomes = Income.objects.filter(date_expired__range=[date_start, date_end])
        monthly_incomes = incomes.aggregate(Sum('logistic_value'))['logistic_value__sum'] if incomes.exists() else 0

        # bills
        bills_pending = Bill.objects.filter(is_paid=False)
        bills_pending_cost = bills_pending.aggregate(Sum('final_value'))['final_value__sum'] if bills_pending.exists() else 0

        # payrolls
        payroll_pending = Payroll.objects.filter(is_paid=False)
        payroll_pending_cost = payroll_pending.aggregate(Sum('final_value'))['final_value__sum'] if payroll_pending.exists() else 0

        # vendors
        vendors_cost = Vendor.objects.all().aggregate(Sum('balance'))['balance__sum'] if Vendor.objects.all().exists() else 0
        last_incomes = Income.objects.all()[:10]

        # costumers
        invoices = Invoice.objects.all()[:10]
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerHomepageView(TemplateView):
    template_name = 'costumer_homepage.html'


@method_decorator(staff_member_required, name='dispatch')
class CostumerListView(ListView):
    template_name = 'list_view.html'
    paginate_by = 50
    model = Costumer

    def get_queryset(self):
        qs = Costumer.objects.all()
        qs = Costumer.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(CostumerListView, self).get_context_data(**kwargs)
        page_title, back_url = 'Πελατες', reverse('costumer_homepage')
        queryset_table = CostumerTable(self.object_list)
        table_title, create_url = 'Λίστα', reverse('costumers_create')
        extra_buttons = True
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerCreateView(CreateView):
    template_name = 'form_view.html'
    model = Costumer
    form_class = CostumerForm
    success_url = reverse_lazy('costumer_list')

    def get_success_url(self):
        add_button = self.request.POST.get('add_button', None)
        if add_button:
            return self.new_instance.get_order_url()
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Πελάτη', reverse('costumer_list')
        add_button, button_title = 'add_button', 'Αποθηκευση και Δημιουργια Παραστατικού'
        context.update(locals())
        return context
    
    def form_valid(self, form):
        self.new_instance = form.save()
        return super(CostumerCreateView, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CostumerDetailView(UpdateView):
    template_name = 'DetailView.html'
    model = Costumer
    form_class = CostumerForm

    def get_success_url(self):
        return self.object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super(CostumerDetailView, self).get_context_data(**kwargs)
        orders = self.object.orders.all()
        payments = self.object.payments.all()
        orders_table = OrderTable(orders)
        payments_table = PaymentTable(payments)
        context.update(locals())
        return context
    
    def form_valid(self, form):
        form.save()
        return super(CostumerDetailView, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CreateOrderFromCostumerView(MyFormMixin, CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('costumer_list')

    def get_initial(self):
        initial = super().get_initial()
        self.costumer = get_object_or_404(Costumer, id=self.kwargs['pk'])
        initial['date'] = datetime.now()
        initial['customer'] = self.costumer
        return initial

    def get_context_data(self, **kwargs):
        context = super(CreateOrderFromCostumerView, self).get_context_data(**kwargs)
        form_title = f'Δημιουργία Παραστατικού -> {self.costumer}'

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreatePaymentFromCostumerView(MyFormMixin, CreateView):
    model = Order
    form_class = PaymentForm
    success_url = reverse_lazy('costumer_list')

    def get_initial(self):
        initial = super().get_initial()
        self.costumer = get_object_or_404(Costumer, id=self.kwargs['pk'])
        initial['date'] = datetime.now()
        initial['customer'] = self.costumer
        initial['value'] = self.costumer.balance
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Δημιουργία Πληρωμής -> {self.costumer}'

        context.update(locals())
        return context


@staff_member_required
def delete_costumer_view(request, pk):
    costumer = get_object_or_404(Costumer, id=pk)
    try:
        costumer.delete()
    except:
        messages.warning(request,' Δεν μπορει να διαγραφει!')
    return redirect(reverse('costumer_list'))


@staff_member_required
def empty_costumer_log_view(request, pk):
    costumer = get_object_or_404(Costumer, id=pk)
    orders = costumer.orders.all()
    payments = costumer.payments.all()
    orders.delete()
    payments.delete()
    return redirect(costumer.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class CreateOrderFromCostumerDetailView(MyFormMixin, CreateView):
    model = Order
    form_class = OrderForm

    def get_success_url(self):
        return self.costumer.get_edit_url()

    def get_initial(self):
        initial = super().get_initial()
        self.costumer = get_object_or_404(Costumer, id=self.kwargs['pk'])
        initial['date'] = datetime.now()
        initial['customer'] = self.costumer
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Δημιουργία Παραστατικού -> {self.costumer}'
        back_url = self.costumer.get_edit_url()
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreatePaymentFromCostumerDetailView(MyFormMixin, CreateView):
    model = Order
    form_class = PaymentForm

    def get_success_url(self):
        return self.costumer.get_edit_url()

    def get_initial(self):
        initial = super().get_initial()
        self.costumer = get_object_or_404(Costumer, id=self.kwargs['pk'])
        initial['date'] = datetime.now()
        initial['customer'] = self.costumer
        initial['value'] = self.costumer.balance
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Δημιουργία Πληρωμής -> {self.costumer}'
        back_url = self.costumer.get_edit_url()
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class EditOrderFromCostumerView(UpdateView):
    model = Order
    template_name = 'form_view.html'
    form_class = OrderForm

    def get_success_url(self):
        return self.object.customer.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = f'Επεξεργασία {self.object}', self.get_success_url()
        delete_url = reverse('delete_order_from_costumer', kwargs={'pk': self.object.id})
        invoice_url = reverse('create_costu_inv_from_order', kwargs={'pk': self.object.id})

        context.update(locals())
        return context


@staff_member_required
def delete_order_from_costumer(request, pk):
    order = get_object_or_404(Order, id=pk)
    order.delete()
    return redirect(order.customer.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class EditPaymentFromCostumerView(UpdateView):
    model = Payment
    template_name = 'form_view.html'
    form_class = PaymentForm

    def get_success_url(self):
        return self.object.customer.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = f'Επεξεργασία {self.object}', self.get_success_url()
        delete_url = reverse('delete_payment_from_costumer', kwargs={'pk': self.object.id})
        context.update(locals())
        return context


@staff_member_required
def delete_payment_from_costumer(request, pk):
    payment = get_object_or_404(Payment, id=pk)
    payment.delete()
    return redirect(payment.customer.get_edit_url())


@staff_member_required
def analysis_view(request):
    date_range = request.GET.get('daterange')
    orders = Order.filters_data(request, Order.objects.all())
    payments = Payment.filters_data(request, Payment.objects.all())
    costumers_orders = orders.values('customer__first_name', 'customer__last_name').annotate(total=Sum('value')).order_by('-total')
    costumers_payments = payments.values('customer__first_name', 'customer__last_name').annotate(total=Sum('value')).order_by('-total')
    total_value = orders.aggregate(Sum('value'))['value__sum'] if orders else 0
    total_payment = payments.aggregate(Sum('value'))['value__sum'] if payments else 0
    difference = total_value - total_payment
    currency = CURRENCY
    context = locals()
    return render(request, 'analysis.html', context)


@method_decorator(staff_member_required, name='dispatch')
class PrintListView(ListView):
    template_name = 'pdf_templates/list.html'

    model = Costumer

    def get_queryset(self):
        qs = Costumer.objects.filter(balance__gt=0)
        qs = Costumer.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(PrintListView, self).get_context_data(**kwargs)
        costumers = Costumer.filters_data(self.request, Costumer.objects.all())
        title = 'Λιστα Πελατών'
        context.update(locals())
        return context


@staff_member_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
