from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import PayrollPersonForm
from django.utils import timezone
from .models import Payroll, Person, BillCategory, Bill
from .forms import BillFromCategoryForm, PersonSheduleForm
from .calendar_model import PersonSchedule

from datetime import datetime


@staff_member_required
def validate_payroll_creation_view(request, pk):
    instance = get_object_or_404(Person, id=pk)
    form = PayrollPersonForm(request.POST or None, initial={'person': instance})
    if form.is_valid():
        form.save()
        messages.success(request, 'Νεα Μισθοδοσια προστεθηκε.')
    else:
        messages.warning(request, 'Κατι πηγε λαθος')
    return redirect(instance.get_card_url())


@staff_member_required
def copy_payroll_view(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    instance.pk = None
    instance.date_expired = datetime.now()
    instance.save()
    messages.success(request, 'Το Παραστατικο αντιγραφηκε')
    return redirect(instance.person.get_card_url())


@staff_member_required
def copy_bill_view(request, pk):
    instance = get_object_or_404(Bill, id=pk)
    instance.pk = None
    instance.date_expired = timezone.now()
    instance.save()
    messages.success(request, 'Το Παραστατικο Αντιγραφηκε.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def action_pay_bill_view(request, pk):
    instance = get_object_or_404(Bill, id=pk)
    instance.is_paid = False if instance.is_paid else True
    instance.save()
    messages.success(request, 'H Εντολή Πληρωθηκε.') if instance.is_paid else messages.warning(request, 'H Εντολη Αποπληρωθηκε')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def action_pay_payroll(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    instance.is_paid = True if not instance.is_paid else False
    instance.save()
    messages.success(request, 'Η εντολή πληρωθηκε') if instance.is_paid else messages.success(request, 'H Πληρωμή ακυρωθηκε')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def action_copy_payroll(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    instance.pk = None
    instance.date_expired = timezone.now()
    instance.save()
    messages.success(request, 'Η Εντολή Αντιγραφηκε')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def validate_payroll_form(request, pk):
    instance = get_object_or_404(BillCategory, id=pk)
    form = BillFromCategoryForm(request.POST or None, initial={'category': instance})
    if form.is_valid():
        form.save()
        messages.success(request, 'Νεο παραστατικο προστεθηκε.')
    return redirect(instance.get_card_url())


@staff_member_required
def validate_edit_bill_form(request, pk):
    instance = get_object_or_404(Bill, id=pk)
    form = BillFromCategoryForm(request.POST or None, instance=instance)
    if form.is_valid():
        print('form success')
        print(form.cleaned_data.get('date_expired'))
        form.save()
        messages.success(request, 'Το Παραστατικο επεξεργαστηκε επιτυχώς')
    else:
        print('error', form.errors)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'), instance.category.get_card_url())


@staff_member_required
def validate_shedule_view(request, pk):
    instance = get_object_or_404(Person, id=pk)
    form = PersonSheduleForm(request.POST or None, initial={'person': instance})
    if form.is_valid():
        form.save()
        messages.success(request, 'Δημιουργηθηκε νεο ωραριο')
        return redirect(instance.get_card_url())
    else:
        messages.warning(request, form.errors)
    return redirect(instance.get_card_url())


@staff_member_required
def delete_schedule_view(request, pk):
    instance = get_object_or_404(PersonSchedule, id=pk)
    instance.delete()
    return redirect(instance.person.get_card_url())


@staff_member_required
def copy_shedule_view(request, pk):
    instance = get_object_or_404(PersonSchedule, id=pk)
    instance.pk = None
    instance.date_start = instance.date_start.replace(day=datetime.now().day)
    instance.date_end = instance.date_end.replace(day=datetime.now().day)
    instance.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))