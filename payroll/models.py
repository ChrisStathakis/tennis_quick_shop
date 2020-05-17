from django.shortcuts import reverse
from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_delete, post_save
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


from .abstract_models import *
from frontend.tools import initial_date

User = get_user_model()
CURRENCY = settings.CURRENCY


class BillCategory(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=150, verbose_name='Ονομασια')
    balance = models.DecimalField(default=0, max_digits=50, decimal_places=2)
    objects = models.Manager()
    # my_query = BillCategoryManager()

    class Meta:
        verbose_name_plural = '4. Λογαριασμοί'

    def save(self, *args, **kwargs):
        bills = self.bills.all()
        total_data = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills else 0
        paid_data = bills.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if bills.filter(
            is_paid=True) else 0
        self.balance = total_data - paid_data
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('payroll_bills:bill_category_update', kwargs={'pk': self.id})

    def get_card_url(self):
        return reverse('payroll_bills:bill_category_card_view', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('payroll_bills:bill_category_delete', kwargs={'pk': self.id})

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    tag_balance.short_description = 'Remaining'

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset


class Bill(DefaultOrderModel):
    title = models.CharField(max_length=150, verbose_name='Τίτλος', blank=True)
    category = models.ForeignKey(BillCategory, null=True,
                                 on_delete=models.PROTECT,
                                 related_name='bills',
                                 verbose_name='Λογαριασμός'
                                 )
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '1. Εντολη Πληρωμης Λογαριασμού'
        verbose_name = 'Λογαριασμός'
        ordering = ['-date_expired']

    def save(self, *args, **kwargs):
        self.final_value = self.value
        if self.is_paid:
            self.paid_value = self.final_value
        if self.id:
            self.title = f'Παραστατικο {self.id}' if not self.title else self.title
        super().save(*args, **kwargs)
        self.category.save()

    def __str__(self):
        return f'{self.category} - {self.title}' if self.category else f'self.title'

    def tag_model(self):
        return f'Bill- {self.category.title}'

    def tag_category(self):
        return f'{self.category.title}'

    def get_edit_url(self):
        return reverse('payroll_bills:bill_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('payroll_bills:bill_delete', kwargs={'pk': self.id})

    def get_modal_url(self):
        return reverse('payroll_bills:ajax_edit_bill', kwargs={'pk': self.id})

    def get_copy_url(self):
        return reverse('payroll_bills:copy_bill_view', kwargs={'pk': self.id})

    def get_pay_url(self):
        return reverse('payroll_bills:action_pay_bill', kwargs={'pk': self.id})

    def update_category(self):
        self.category.update_balance()

    @staticmethod
    def filters_data(request, queryset):
        paid_name = request.GET.getlist('paid_name', None)
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        bill_name = request.GET.getlist('bill_name', None)
        date_start, date_end, date_range = initial_date(request, 6)
        queryset = queryset.filter(date_expired__range=[date_start, date_end]) if date_start else queryset
        queryset = queryset.filter(is_paid=True) if 'have_' in paid_name else queryset.filter(is_paid=False) \
            if 'not_' in paid_name else queryset
        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(category__id__in=bill_name) if bill_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name) |
                                   Q(category__title__icontains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset

    # report
    
    @property
    def report_date(self):
        return self.date_expired

    def report_expense_type(self):
        return f'Λογαριαμος-{self.category.title}'

    def report_value(self):
        return self.final_value


@receiver(post_delete, sender=Bill)
def update_billing(sender, instance, **kwargs):
    instance.category.save()


class Occupation(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64, verbose_name='Απασχόληση')
    notes = models.TextField(blank=True, null=True, verbose_name='Σημειώσεις')
    balance = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Υπόλοιπο')

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "5. Απασχόληση"
        verbose_name = 'Απασχόληση'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.balance = self.person_set.all().aggregate(Sum('balance'))['balance__sum'] \
            if self.person_set.all().exists() else 0
        super().save(*args, *kwargs)

    def tag_balance(self):
        return '%s %s' % (self.balance, CURRENCY)

    tag_balance.short_description = 'Υπόλοιπο'

    def get_edit_url(self):
        return reverse('payroll_bills:occupation_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('payroll_bills:occupation_delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset


class Person(models.Model):
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=64, unique=True, verbose_name='Ονοματεπώνυμο')
    phone = models.CharField(max_length=10, verbose_name='Τηλέφωνο', blank=True)
    phone1 = models.CharField(max_length=10, verbose_name='Κινητό', blank=True)
    date_added = models.DateField(default=timezone.now, verbose_name='Ημερομηνία Πρόσληψης')
    occupation = models.ForeignKey(Occupation, null=True, verbose_name='Απασχόληση', on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Υπόλοιπο')
    vacation_days = models.IntegerField(default=0, verbose_name='Συνολικές Μέρες Αδειας')

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "6. Υπάλληλος"
        verbose_name = 'Υπάλληλος'

    def save(self, *args, **kwargs):
        self.balance = self.update_balance()
        super().save(*args, **kwargs)
        self.occupation.save() if self.occupation else ''

    def update_balance(self):
        queryset = self.person_invoices.all()
        value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.aggregate(Sum('paid_value'))['paid_value__sum'] if queryset else 0
        diff = value - paid_value
        return diff

    def __str__(self):
        return self.title

    def tag_balance(self):
        return '%s %s' % (self.balance, CURRENCY)

    def tag_occupation(self):
        return f'{self.occupation.title}'

    def get_edit_url(self):
        return reverse('payroll_bills:person_update', kwargs={'pk': self.id})

    def get_card_url(self):
        return reverse('payroll_bills:person_card', kwargs={'pk': self.id})

    def get_copy_url(self):
        return reverse('payroll_bills:copy_payroll', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('payroll_bills:person_delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        occup_name = request.GET.getlist('occup_name', None)
        date_range = request.GET.get('date_range')
        print('date', date_range)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(occupation__id__in=occup_name) if occup_name else queryset
        return queryset


class PayrollInvoiceManager(models.Manager):
    def invoice_per_person(self, instance):
        return super(PayrollInvoiceManager, self).filter(person=instance)

    def not_paid(self):
        return super(PayrollInvoiceManager, self).filter(is_paid=False)


class Payroll(DefaultOrderModel):
    title = models.CharField(max_length=150, verbose_name='Τίτλος', blank=True)
    person = models.ForeignKey(Person, verbose_name='Υπάλληλος', on_delete=models.PROTECT,
                               related_name='person_invoices')
    category = models.CharField(max_length=1, choices=PAYROLL_CHOICES, default='1', verbose_name='Κατηγορια')
    objects = models.Manager()


    class Meta:
        verbose_name_plural = '2. Μισθόδοσία'
        verbose_name = 'Εντολή Πληρωμής'
        ordering = ['is_paid', '-date_expired', ]

    def __str__(self):
        return '%s %s' % (self.date_expired, self.person.title)

    def save(self, *args, **kwargs):
        self.final_value = self.value
        self.paid_value = self.final_value if self.is_paid else 0
        if self.id:
            self.title = f'Μισθοδοσια {self.id}' if not self.title else self.title
        super(Payroll, self).save(*args, **kwargs)
        self.person.save()

    def tag_model(self):
        return f'Payroll - {self.person.title}'

    def tag_person(self):
        return f'{self.person.title}'

    def get_edit_url(self):
        return reverse('payroll_bills:payroll_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('payroll_bills:payroll_delete', kwargs={'pk': self.id})

    def get_card_url(self):
        return reverse('payroll_bills:person_card', kwargs={'pk': self.id})

    def get_edit_card_url(self):
        return reverse('payroll_bills:payroll_card_update', kwargs={'pk': self.id})

    def get_delete_card_url(self):
        return reverse('payroll_bills:payroll_card_delete', kwargs={'pk': self.id})

    def get_pay_url(self):
        return reverse('payroll_bills:action_pay_payroll', kwargs={'pk': self.id})

    def get_copy_url(self):
        return reverse('payroll_bills:action_copy_payroll', kwargs={'pk': self.id})

    def update_category(self):
        self.person.update_balance()

    def destroy_payments(self):
        queryset = self.payment_orders.all()
        for payment in queryset:
            payment.delete()

    @property
    def date(self):
        return self.date_expired

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    tag_value.short_description = 'Αξία Παραστατικού'

    def tag_is_paid(self):
        return "Is Paid" if self.is_paid else "Not Paid"

    def get_remaining_value(self):
        return self.final_value - self.paid_value

    def tag_remaining_value(self):
        return '%s %s' % (self.get_remaining_value(), CURRENCY)

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        person_name = request.GET.getlist('person_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        occup_name = request.GET.getlist('cate_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        date_start, date_end, date_range = initial_date(request, 6)

        queryset = queryset.filter(date_expired__range=[date_start, date_end]) if date_start and date_end else queryset
        queryset = queryset.filter(is_paid=True) if 'paid' in paid_name else queryset.filter(is_paid=False) \
            if 'not_' in paid_name else queryset
        queryset = queryset.filter(category__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(person__id__in=person_name) if person_name else queryset
        queryset = queryset.filter(person__occupation__id__in=occup_name) if occup_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name) |
                                   Q(person__title__icontains=search_name) |
                                   Q(person__occupation__title__icontains=search_name)
                                   ).distict() if search_name else queryset

        return queryset

    @property
    def report_date(self):
        return self.date_expired

    def report_expense_type(self):
        return f'Μισθοδοσια-{self.person} - {self.get_category_display()}'

    def report_value(self):
        return self.value


@receiver(post_delete, sender=Payroll)
def update_person_on_delete(sender, instance, *args, **kwargs):
    person = instance.person
    person.balance -= instance.final_value - instance.paid_value
    person.save()


class GenericExpenseCategory(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '7. Γενικά Έξοδα'
        verbose_name = 'Έξοδο'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        orders = self.expenses.all()
        self.balance = orders.aggregate(Sum('final_value'))['final_value__sum'] if orders else 0
        self.balance -= orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders else 0
        super(GenericExpenseCategory, self).save(*args, *kwargs)

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def get_dashboard_url(self):
        return reverse('billings:expense_cate_detail', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)

        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset


class GenericExpense(DefaultOrderModel):
    category = models.ForeignKey(GenericExpenseCategory,
                                 null=True,
                                 on_delete=models.PROTECT,
                                 related_name='expenses'
                                 )
    objects = models.Manager()

    def tag_model(self):
        return f'Expenses- {self.category}'

    class Meta:
        verbose_name_plural = '3. Εντολή Πληρωμής Γενικών Εξόδων'
        verbose_name = 'Εντολή Πληρωμής'
        ordering = ['is_paid', '-date_expired']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.final_value = self.value
        self.paid_value = self.final_value if self.is_paid else 0
        super().save(*args, **kwargs)
        self.category.save()

    def get_dashboard_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'edit', 'mymodel': 'expense'})

    def get_paid_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'paid', 'mymodel': 'expense'})

    def get_delete_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'delete', 'mymodel': 'expense'})

    def get_dashboard_save_as_url(self):
        return reverse('billings:save_as_view', kwargs={'pk': self.id, 'slug': 'expense'})

    def get_dashboard_list_url(self):
        return reverse('billings:expenses_list')

    def update_category(self):
        self.category.update_balance()

    def destroy_payments(self):
        queryset = self.payment_orders.all()
        for payment in queryset:
            payment.delete()

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        date_start, date_end = request.GET.get('date_start', None), request.GET.get('date_end', None)

        if date_start and date_end and date_end > date_start:
            queryset = queryset.filter(date_expired__range=[date_start, date_end])
        queryset = queryset.filter(is_paid=True) if 'paid' in paid_name else queryset.filter(is_paid=False) \
            if 'not_paid' in paid_name else queryset
        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name) |
                                   Q(category__title__icontains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset


@receiver(post_delete, sender=GenericExpense)
def update_expense_category(sender, instance, **kwargs):
    instance.category.update_balance()


@receiver(pre_delete, sender=GenericExpense)
def delete_generic_order_items(sender, instance, **kwargs):
    for order in instance.payment_orders.all(): order.delete()





