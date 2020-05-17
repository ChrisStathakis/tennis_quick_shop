from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

from django_tables2 import RequestConfig


from .models import Order, Payment
from .tables import OrderTableListView, PaymentTableListView
from .forms import OrderMainForm, OrderForm, PaymentForm, MainPaymentForm


@method_decorator(staff_member_required, name='dispatch')
class OrderListView(ListView):
    model = Order
    template_name = 'list_view.html'
    paginate_by = 30

    def get_queryset(self):
        qs = Order.objects.filter(customer__active=True)
        qs = Order.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = OrderTableListView(self.object_list)
        page_title, create_url = 'Παραστατικά', reverse('orders:order_create')
        RequestConfig(self.request).configure(queryset_table)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class OrderCreateView(CreateView):
    model = Order
    template_name = 'form_view.html'
    success_url = reverse_lazy('orders:home')
    form_class = OrderMainForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Παραστατικού', self.success_url
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class OrderUpdateView(UpdateView):
    model = Order
    template_name = 'form_view.html'
    success_url = reverse_lazy('orders:home')
    form_class = OrderForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = f'Επεξεργασία {self.object}', self.success_url
        delete_url, customer_url = self.object.get_delete_url(), self.object.customer.get_edit_url()
        context.update(locals())
        return context


@staff_member_required
def delete_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    order.delete()
    return redirect(reverse('orders:home'))


@method_decorator(staff_member_required, name='dispatch')
class PaymentListView(ListView):
    model = Payment
    template_name = 'list_view.html'
    paginate_by = 25

    def get_queryset(self):
        qs = Payment.objects.all()
        qs = Payment.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = PaymentTableListView(self.object_list)
        page_title, create_url = 'Πληρωμές', reverse('orders:payment_create')
        RequestConfig(self.request).configure(queryset_table)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class PaymentCreateView(CreateView):
    model = Payment
    template_name = 'form_view.html'
    success_url = reverse_lazy('orders:payment_home')
    form_class = MainPaymentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Πληρωμής', self.success_url
        context.update(locals())
        return context

    def form_valid(self, form):
        print('form valid')
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


@method_decorator(staff_member_required, name='dispatch')
class PaymentUpdateView(UpdateView):
    model = Payment
    template_name = 'form_view.html'
    success_url = reverse_lazy('orders:payment_home')
    form_class = PaymentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = f'Επεξεργασία {self.object}', self.success_url
        delete_url, customer_url = self.object.get_delete_url(), self.object.customer.get_edit_url()
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@staff_member_required
def delete_payment(request, pk):
    payment = get_object_or_404(Payment, id=pk)
    payment.delete()
    return redirect(reverse('orders:payment_home'))
