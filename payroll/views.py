from django.shortcuts import render, reverse, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django_tables2 import RequestConfig

from .models import Payroll, Occupation, Person, PAYROLL_CHOICES
from .forms import PayrollForm, PersonForm, OccupationForm, PayrollPersonForm, CreateManyInvoicesForm, PersonSheduleForm
from .tables import PayrollTable, PersonTable, OccupationTable, PayrollCardTable, PersonScheduleTable
from .calendar_model import PersonSchedule
from datetime import timedelta
from dateutil.relativedelta import relativedelta


@method_decorator(staff_member_required, name='dispatch')
class HomepageView(TemplateView):
    template_name = 'payroll/homepage.html'


@method_decorator(staff_member_required, name='dispatch')
class PayrollListView(ListView):
    template_name = 'payroll/list.html'
    model = Payroll
    paginate_by = 50

    def get_queryset(self):
        qs = Payroll.objects.all()
        self.initial_data = qs
        qs = Payroll.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(PayrollListView, self).get_context_data(**kwargs)
        qs_table = PayrollTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(qs_table)
        context['create_url'] = reverse('payroll_bills:payroll_create')
        context['back_url'] = reverse('payroll_bills:home')
        context['queryset_table'] = qs_table
        context['payroll'] = True
        persons_ids = self.initial_data.values_list('person')
        context['persons'] = Person.objects.filter(id__in=persons_ids)
        context['categories'] = PAYROLL_CHOICES
        context['date_filter'], context['search_filter'], context['person_cate_filter'], context['person_filter'] \
            = [True] * 4
        context['form_button'] = True
        context['create_form'] = CreateManyInvoicesForm
        return context


@method_decorator(staff_member_required, name='dispatch')
class PayrollCreateView(CreateView):
    template_name = 'payroll/form.html'
    form_class = PayrollForm
    model = Payroll
    success_url = reverse_lazy('payroll_bills:payroll_list')

    def get_context_data(self, **kwargs):
        context = super(PayrollCreateView, self).get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['form_title'] = 'Δημιουργια Μισθοδοσιας'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νεα μισθοδοσια Δημιουργηθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class PayrollUpdateView(UpdateView):
    template_name = 'payroll/form.html'
    form_class = PayrollForm
    model = Payroll
    success_url = reverse_lazy('payroll_bills:payroll_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse('payroll_bills:payroll_list')
        context['form_title'] = f'{self.object}'
        context['delete_url'] = self.object.get_delete_url()
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η μισθοδοσια επεξεργαστηκε.')
        return super().form_valid(form)


@staff_member_required
def payroll_delete_view(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    instance.delete()
    messages.warning(request, 'Το Παραστατικο διαγραφηκε.')
    return redirect(reverse('payroll_bills:payroll_list'))


@staff_member_required
def create_many_payroll_view(request):
    form = CreateManyInvoicesForm(request.GET or None)
    if form.is_valid():
        date_type = form.cleaned_data.get('date_type')
        value = form.cleaned_data.get('value')
        repeat = form.cleaned_data.get('repeat')
        invoices_ids = request.GET.getlist('invoice_name')
        for id in invoices_ids:
            payroll = get_object_or_404(Payroll, id=id)
            if date_type == 'a':
                for ele in range(repeat):
                    new_value = (ele+1) * value
                    Payroll.objects.create(
                        date_expired=payroll.date_expired + timedelta(days=new_value),
                        person=payroll.person,
                        value=payroll.value,
                        is_paid=payroll.is_paid,
                        category=payroll.category,
                        title=payroll.title
                    )
            if date_type == 'b':
                for ele in range(repeat):
                    new_value = (ele+1) * value
                    Payroll.objects.create(
                        date_expired=payroll.date_expired + relativedelta(months=new_value),
                        person=payroll.person,
                        value=payroll.value,
                        is_paid=payroll.is_paid,
                        category=payroll.category,
                        title=payroll.title
                    )

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@method_decorator(staff_member_required, name='dispatch')
class PersonCardView(DetailView):
    model = Person
    template_name = 'payroll/person_card.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_filter'] = True
        context['page_title'] = self.object
        context['form'] = PayrollPersonForm(initial={'person': self.object})
        context['calendar_form'] = PersonSheduleForm(initial={'person': self.object})
        payroll_qs = Payroll.filters_data(self.request, Payroll.objects.filter(person=self.object))
        events_qs = PersonSchedule.filters_data(self.request, self.object.schedules.all())

        context['total_payroll'] = payroll_qs.aggregate(Sum('value'))['value__sum'] if payroll_qs.exists() else 0
        context['total_hours'] = events_qs.aggregate(Sum('hours'))['hours__sum'] if events_qs.exists() else 0
        context['queryset_table'] = PayrollCardTable(payroll_qs)
        context['schedule_table'] = PersonScheduleTable(events_qs)

        return context


@method_decorator(staff_member_required, name='dispatch')
class PersonListView(ListView):
    template_name = 'payroll/list.html'
    model = Person
    paginate_by = 50

    def get_queryset(self):
        qs = Person.objects.all()
        qs = Person.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse('payroll_bills:person_create')
        context['back_url'] = reverse('payroll_bills:home')
        context['queryset_table'] = PersonTable(self.object_list)
        context['page_title'] = 'Υπαλληλοι'
        return context


@method_decorator(staff_member_required, name='dispatch')
class PersonCreateView(CreateView):
    template_name = 'payroll/form.html'
    form_class = PersonForm
    model = Person
    success_url = reverse_lazy('payroll_bills:person_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['form_title'] = 'Δημιουργια Υπαλληλου'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νεος Υπαλληλος Δημιουργηθηκε.')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class PersonUpdateView(UpdateView):
    template_name = 'payroll/form.html'
    form_class = PersonForm
    model = Person
    success_url = reverse_lazy('payroll_bills:person_list')

    def get_context_data(self, **kwargs):
        context = super(PersonUpdateView, self).get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url
        context['form_title'] = f'Επεξεργασια Υπαλληλου {self.object}'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Ο Υπαλληλος επεξεργαστηκε επιτιχώς')
        return super().form_valid(form)


@staff_member_required
def person_delete_view(request, pk):
    instance = get_object_or_404(Person, id=pk)
    instance.delete()
    messages.warning(request, 'O υπαλληλος διαγραφηκε')
    return redirect(reverse('payroll_bills:person_list'))


@method_decorator(staff_member_required, name='dispatch')
class OccupationListView(ListView):
    template_name = 'payroll/list.html'
    model = Occupation
    paginate_by = 50

    def get_queryset(self):
        qs = Occupation.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse('payroll_bills:occupation_create')
        context['back_url'] = reverse('payroll_bills:home')
        context['queryset_table'] = OccupationTable(self.object_list)
        return context


@method_decorator(staff_member_required, name='dispatch')
class OccupationCreateView(CreateView):
    template_name = 'payroll/form.html'
    form_class = OccupationForm
    model = Occupation
    success_url = reverse_lazy('payroll_bills:occupation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['form_title'] = 'Δημιουργια Επαγγελματος'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νεο επαγγελμα δημιουργηθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class OccupationUpdateView(UpdateView):
    template_name = 'payroll/form.html'
    form_class = OccupationForm
    model = Occupation
    success_url = reverse_lazy('payroll_bills:occupation_list')

    def get_context_data(self, **kwargs):
        context = super(OccupationUpdateView, self).get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        context['form_title'] = f'Επεξεργασια {self.object}'
        return context

    def form_valid(self, form):
        form.save(form)
        messages.success(self.request, 'To Επαγγελμα επεξεργαστηκε.')
        return super().form_valid(form)


@staff_member_required
def occupation_delete_view(request, pk):
    instance = get_object_or_404(Occupation, id=pk)
    instance.delete()
    messages.warning(request, 'Το επαγγελμα διαγράφηκε.')
    return redirect(reverse('payroll_bills:payroll_list'))


@method_decorator(staff_member_required, name='dispatch')
class PayrollCardUpdateView(UpdateView):
    template_name = 'payroll/form.html'
    form_class = PayrollForm
    model = Payroll
    
    def get_success_url(self):
        return self.object.person.get_card_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.get_success_url()
        context['form_title'] = f'{self.object}'
        context['delete_url'] = self.object.get_delete_card_url()
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η μισθοδοσια επεξεργαστηκε.')
        return super().form_valid(form)


@staff_member_required
def payrollCard_delete_view(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    instance.delete()
    messages.warning(request, 'Το Παραστατικο διαγραφηκε.')
    return redirect(instance.person.get_card_url())

from operator import attrgetter
from itertools import chain


@staff_member_required
def calendar_view(request, pk):
    instance = get_object_or_404(Person, id=pk)
    events = PersonSchedule.filters_data(request, instance.schedules.all())
    payrolls = Payroll.filters_data(request, instance.person_invoices.all())
    qs_data =  sorted(
                chain(events, payrolls,),
                key=attrgetter('date'))
    total_hours = events.aggregate(Sum('hours'))['hours__sum'] if events.exists() else 0
    date_filter = True
    return render(request, 'payroll/calendar.html', context=locals())