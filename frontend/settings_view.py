from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Sum
from django.conf import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta

from frontend.models import PaymentMethod
from .tables import PaymentMethodTable
from .forms import PaymentMethodForm
CURRENCY = settings.CURRENCY


@method_decorator(staff_member_required, name='dispatch')
class PaymentMethodListView(ListView):
    model = PaymentMethod
    template_name = 'list_view.html'
    paginate_by = 50

    def get_queryset(self):
        qs = self.model.filters_data(self.request, self.model.objects.all())
        return qs

    def get_context_data(self, *args,  **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['queryset_table'] = PaymentMethodTable(self.object_list)
        context['create_url'] = reverse('payment_method_create')
        return context


@method_decorator(staff_member_required, name='dispatch')
class PaymentMethodCreateView(CreateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'form_view.html'
    success_url = reverse_lazy('payment_method_list')

    def get_context_data(self, **kwargs):
        context = super(PaymentMethodCreateView, self).get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργια Τροπου Πληρωμης', self.success_url

        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Ο Τροπος Πληρωμης δημιουργηθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class PaymentMethodUpdateView(UpdateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    success_url = reverse_lazy('payment_method_list')
    template_name = 'form_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'], context['back_url'] = f'Επεξεργασια {self.object.title}', self.success_url
        context['delete_url'] = self.object.get_delete_url
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Ο τροποσ πληρωμης επεξεργαστηκε επιτυχως')
        return super().form_valid(form)


@staff_member_required
def payment_method_delete_view(request, pk):
    instance = get_object_or_404(PaymentMethod, id=pk)
    try:
        instance.delete()
    except:
        messages.warning(request, ''
                                  'Δε μπορειτε να διαγραψετε αυτον τον τροπο πληρωμης επειδη χρησιμοποιειται')
    return redirect(reverse('payment_method_list'))