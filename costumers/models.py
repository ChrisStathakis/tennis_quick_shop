from django.db import models
from django.utils import timezone
from django.db.models import Q, Sum
from django.conf import settings
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.shortcuts import get_object_or_404

from tinymce.models import HTMLField

from frontend.models import PaymentMethod

from decimal import Decimal
CURRENCY = settings.CURRENCY


class MyCard(models.Model):
    favorite = models.BooleanField(default=False, verbose_name='Προτεινομενο')
    title = models.CharField(unique=True, max_length=200, verbose_name='Τιτλος')
    eponimia = models.CharField(max_length=200, verbose_name='Επωνυμια')
    job = models.TextField(verbose_name='Περιγραφη Επαγγελματος')
    afm = models.CharField(max_length=10, verbose_name='ΑΦΜ')
    doy = models.CharField(max_length=150, verbose_name='ΔΟΥ')
    city = models.CharField(max_length=150, verbose_name='Εδρα')
    zipcode = models.CharField(max_length=10, verbose_name='TK')
    phone = models.CharField(max_length=100, verbose_name='Τηλεφωνα')
    fax = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.title


class Costumer(models.Model):
    eponimia = models.CharField(null=True, max_length=240, verbose_name='Επωνυμια')
    address = models.CharField(blank=True, null=True, max_length=240, verbose_name='Διευθυνση')
    job_description = models.CharField(blank=True, null=True, max_length=240, verbose_name='Επαγγελμα')
    loading_place = models.CharField(blank=True, null=True, max_length=240, default='Εδρα μας', verbose_name='Τοπος Φορτωσης')
    destination = models.CharField(blank=True, null=True, max_length=240, default='Εδρα του,', verbose_name='Προορισμος')
    afm = models.CharField(blank=True, null=True, max_length=10, verbose_name='ΑΦΜ')
    doy = models.CharField(blank=True, null=True, max_length=240, default='Σπαρτη', verbose_name='ΔΟΥ')
    destination_city =  models.CharField(blank=True, null=True, max_length=240 , verbose_name='Πολη')
    transport = models.CharField(blank=True, null=True, max_length=10, verbose_name='Μεταφορικο Μεσο')

    first_name = models.CharField(max_length=200, verbose_name='Ονομα', blank=True)
    last_name = models.CharField(max_length=200, verbose_name='Επιθετο', blank=True)
    amka = models.CharField(max_length=20, blank=True, verbose_name='Ψευδονυμο')
    notes = models.CharField(max_length=200, blank=True, verbose_name='Σημειώσεις')
    cellphone = models.CharField(max_length=20, blank=True, verbose_name='Κινητό')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Τηλέφωνο')
    active = models.BooleanField(default=True, verbose_name='Ενεργός')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    paid_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    balance = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)

    class Meta:
        ordering = ['eponimia', 'afm']

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        if not self.eponimia:
            self.eponimia = f'{self.first_name} {self.last_name}'
        self.balance = self.value - self.paid_value
        super(Costumer, self).save(*args, **kwargs)

    def __str__(self):
        return self.eponimia



    def update_orders(self):
        qs = self.orders.all()
        new_value = qs.aggregate(Sum('value'))['value__sum'] if qs.exists() else 0
        self.value = new_value
        self.save()

    def update_payments(self):
        qs = self.payments.all()
        new_value = qs.aggregate(Sum('value'))['value__sum'] if qs.exists() else 0
        self.paid_value = new_value
        self.save()

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_paid_value(self):
        return f'{self.paid_value} {CURRENCY}'

    def phones(self):
        return f'{self.cellphone} {self.phone}'

    def get_edit_url(self):
        return reverse('costumer_detail', kwargs={'pk': self.id})

    def get_order_url(self):
        return reverse('create_order_costumer_view', kwargs={'pk': self.id})

    def get_payment_url(self):
        return reverse('create_payment_costumer_view', kwargs={'pk': self.id})

    def get_quick_view_url(self):
        return reverse('costumer_quick_view', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        q = request.GET.get('q', None)
        balance_name = request.GET.get('balance_name', None)
        status_name = request.GET.get('active_name', None)
        queryset = queryset.filter(active=True) if status_name else queryset
        queryset = queryset.filter(balance__gt=Decimal('0.00')) if balance_name else queryset
        queryset = queryset.filter(Q(first_name__startswith=q.capitalize()) |
                                   Q(last_name__startswith=q.capitalize()) |
                                   Q(eponimia__icontains=q) |
                                   Q(amka__icontains=q) |
                                   Q(afm__icontains=q) |
                                   Q(cellphone__icontains=q) |
                                   Q(phone__icontains=q)
                                   ).distinct() if q else queryset
        return queryset


class PaymentInvoice(models.Model):
    SERIES = (
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'Γ')
    )
    TYPE_ = (
        ('a', 'Τιμολογιο'),
        ('b', 'Δελτιο Παραγγελίας'),
        ('c', 'Προπαραγγελία')
    )
    locked = models.BooleanField(default=False, verbose_name="Κλειδωμενο")
    payment_info = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True, verbose_name='Τρόπος Πληρωμής')
    card_info = models.ForeignKey(MyCard, null=True, on_delete=models.PROTECT, verbose_name='Στάμπα')
    order_type = models.CharField(default='a', max_length=1, choices=TYPE_, verbose_name='Ειδος Παραστατικου')
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT, null=True, verbose_name='Πελάτης')
    number = models.IntegerField(blank=True, null=True)
    series = models.CharField(max_length=1, choices=SERIES, verbose_name='Σειρά')
    place = models.CharField(max_length=220, blank=True)
    date = models.DateTimeField(verbose_name='Ημερομηνία', default=timezone.now())

    value = models.DecimalField(decimal_places=2, max_digits=17, default=0.00, verbose_name='Αξια Προ Εκπτωσεως')
    discount_value = models.DecimalField(decimal_places=2, max_digits=17, default=0.00, verbose_name='Εκπτωση')
    clean_value = models.DecimalField(decimal_places=2, max_digits=17, default=0.00, verbose_name='Καθαρη Αξια')
    taxes_value = models.DecimalField(decimal_places=2, max_digits=17, default=0.00, verbose_name='Συνολο ΦΠΑ')

    charges_cost = models.DecimalField(decimal_places=2, max_digits=17, default=0.00, verbose_name='επιβαρυνσεις')
    charges_taxes = models.DecimalField(decimal_places=2, max_digits=17, default=0.00, verbose_name='επιβαρυνσεις ΦΠΑ')

    total_value = models.DecimalField(decimal_places=2, max_digits=17, default=0, verbose_name='Πληρωτεο Ποσο')

    final_value = models.DecimalField(decimal_places=2, max_digits=17, default=0, verbose_name='Τελική Αξία')
    notes = HTMLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        items = self.order_items.all()
        self.value = items.aggregate(Sum('clean_value'))['clean_value__sum'] if items.exists() else 0
        self.discount_value = items.aggregate(Sum('discount_value'))['discount_value__sum'] if items.exists() else 0
        self.clean_value = self.value - self.discount_value
        self.taxes_value = items.aggregate(Sum('taxes_value'))['taxes_value__sum'] if items.exists() else 0
        self.total_value = items.aggregate(Sum('total_value'))['total_value__sum'] if items.exists() else 0
        self.final_value = self.total_value + Decimal(self.charges_cost) + Decimal(self.charges_taxes)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['number', 'series', 'order_type']
        ordering = ['-id']

    def __str__(self):
        return f'{self.get_series_display()} | {self.number}'

    def tag_title(self):
        return self.__str__()

    def unique_number(self):
        qs = PaymentInvoice.objects.filter(series=self.series)
        if qs.exists():
            number = qs.count()
            return number
        return 1

    def get_edit_url(self):
        return reverse('costumers:payment_invoice_update', kwargs={'pk': self.id})

    def tag_value(self):
        return str(self.value).replace('.', ',')

    def tag_discount_value(self):
        return str(self.discount_value).replace('.', ',')

    def tag_total_value(self):
        return str(self.total_value).replace('.', ',')

    def tag_clean_value(self):
        return str(self.clean_value).replace('.', ',')

    def tag_taxes_value(self):
        return str(self.taxes_value).replace('.', ',')

    def tag_final_value(self):
        return str(self.final_value).replace('.', ',')

    def tag_charges_cost(self):
        return str(self.charges_cost).replace('.', ',')


class CostumerDetails(models.Model):
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT)
    invoice = models.OneToOneField(PaymentInvoice, on_delete=models.CASCADE, related_name='profile')
    eponimia = models.CharField(null=True, max_length=240, verbose_name='Επωνυμια')
    address = models.CharField(blank=True, null=True, max_length=240, verbose_name='Διευθυνση')
    job_description = models.CharField(blank=True, null=True, max_length=240, verbose_name='Επαγγελμα')
    loading_place = models.CharField(blank=True, null=True, max_length=240, default='Εδρα μας',
                                     verbose_name='Τοπος Φορτωσης')
    destination = models.CharField(blank=True, null=True, max_length=240, default='Εδρα του,',
                                   verbose_name='Προορισμος')
    afm = models.CharField(blank=True, null=True, max_length=10, verbose_name='ΑΦΜ')
    doy = models.CharField(blank=True, null=True, max_length=240, default='Σπαρτη', verbose_name='ΔΟΥ')
    destination_city = models.CharField(blank=True, null=True, max_length=240, verbose_name='Πολη')
    transport = models.CharField(blank=True, null=True, max_length=10, verbose_name='Μεταφορικο Μεσο')
    phone = models.CharField(blank=True, null=True, max_length=200, verbose_name='Τηλεφωνα')

    def __str__(self):
        return self.costumer.eponimia


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(PaymentInvoice, on_delete=models.CASCADE, related_name='order_items')
    UNITS = (
        ('a', 'Τεμάχιο'),
        ('b', 'Κιβώτιο'),
        ('c', 'Κιλό'),

    )

    title = models.CharField(max_length=250, verbose_name='Περιγραφη')
    unit = models.CharField(max_length=1, choices=UNITS, default='a', verbose_name='ΜΜ')

    qty = models.DecimalField(max_digits=17, decimal_places=2, default=1, verbose_name='Ποσότητα')
    value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Τιμή')

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Εκπτωση')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Ποσο Εκπτωσης')

    clean_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Αξια')
    total_clean_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Καθαρη Αξια')
    taxes_modifier = models.IntegerField(default=24, verbose_name='ΦΠΑ')
    taxes_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Αξια ΦΠΑ')
    total_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Τελικη Αξία')

    def save(self, *args, **kwargs):

        self.clean_value = self.qty * self.value
        self.discount_value = self.clean_value * Decimal(self.discount/100)

        self.total_clean_value = self.clean_value - self.discount_value
        self.taxes_value = self.total_clean_value * Decimal(self.taxes_modifier/100)
        self.total_value = self.total_clean_value + self.taxes_value

        super().save(*args, **kwargs)
        self.invoice.save()

    def tag_value(self):
        str_value = str(self.value).replace('.', ',')
        return str_value

    def tag_clean_value(self):
        return str(self.clean_value).replace('.', ',')

    def tag_total_value(self):
        return str(self.total_clean_value).replace('.', ',')

    def tag_discount(self):
        return str(self.discount).replace('.', ',')


@receiver(post_save, sender=PaymentInvoice)
def create_unique_number(sender, instance, created, **kwargs):
    if created:
        instance.number = PaymentInvoice.objects.filter(series=instance.series, order_type=instance.order_type).count()
        instance.save()


@receiver(post_save, sender=PaymentInvoice)
def create_costumer_profile(sender, instance, **kwargs):
    profile, created = CostumerDetails.objects.get_or_create(invoice=instance, costumer=instance.costumer)
    if created:
        costumer = instance.costumer
        profile.costumer = costumer
        profile.eponimia = costumer.eponimia
        profile.address = costumer.address
        profile.job_description = costumer.job_description
        profile.loading_place = costumer.loading_place
        profile.destination = costumer.destination
        profile.afm = costumer.afm
        profile.doy = costumer.doy
        profile.destination_city = costumer.destination_city
        profile.transport = costumer.transport
        profile.phone = costumer.phone
        profile.save()


@receiver(post_delete, sender=InvoiceItem)
def delete_invoice_item(sender, instance, **kwargs):
    instance.invoice.save()