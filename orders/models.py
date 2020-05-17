from django.db import models
from costumers.models import Costumer
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.db.models import Q

from tinymce.models import HTMLField
import datetime
CURRENCY = settings.CURRENCY


class Order(models.Model):
    favorite = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Costumer, on_delete=models.CASCADE, related_name='orders', verbose_name='Πελάτης')
    date = models.DateField(verbose_name='Ημερομηνία')
    title = models.CharField(max_length=200, blank=True, verbose_name='Τίτλος')
    description = HTMLField(blank=True, verbose_name='Περιγραφή')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00, verbose_name='Ποσό')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.customer} - {self.title}'

    def save(self, *args, **kwargs):
        if self.id:
            self.title = f'Παραστατικο {self.id}' if len(self.title) == 0 else self.title
        super().save(*args, **kwargs)
        self.customer.update_orders()

    def tag_value(self):
        return f'{self.value} {CURRENCY}'
    
    def get_edit_url(self):
        return reverse('orders:order_update', kwargs={'pk': self.id})

    def get_edit_costumer_url(self):
        return reverse('edit_order_from_costumer', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('orders:order_delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        q = request.GET.get('q', None)
        if q:
            qs = qs.filter(Q(customer__first_name__icontains=q) |
                           Q(customer__last_name__icontains=q) |
                           Q(customer__amka__icontains=q) |
                           Q(customer__cellphone__icontains=q) |
                           Q(customer__phone__icontains=q)
                           ).distinct()
        date_range = request.GET.get('date_range', None)
        if date_range:
            date_range = date_range.split('-')
            date_range[0] = date_range[0].replace(' ', '')
            date_range[1] = date_range[1].replace(' ', '')
            try:
                date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
            except:
                date_start = datetime.datetime.now()
                date_end = datetime.datetime.now()

            qs = qs.filter(date__range=[date_start, date_end])
        return qs


class Payment(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Costumer, on_delete=models.CASCADE, related_name='payments', verbose_name='Πελάτης')
    date = models.DateField(verbose_name='Ημερομηνία')
    title = models.CharField(max_length=200, blank=True, verbose_name='Τίτλος')
    description = models.TextField(blank=True, verbose_name='Περιγραφή')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00, verbose_name='Ποσό')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.id:
            self.title = f'Πληρωμή {self.id}' if len(self.title) == 0 else self.title
        super().save(*args, **kwargs)
        self.customer.update_payments()

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def get_edit_url(self):
        return reverse('orders:payment_update', kwargs={'pk': self.id})

    def get_edit_costumer_url(self):
        return reverse('edit_payment_from_costumer', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('orders:payment_delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        q = request.GET.get('q', None)
        if q:
            qs = qs.filter(Q(customer__first_name__icontains=q) |
                      Q(customer__last_name__icontains=q) |
                      Q(customer__amka__icontains=q) |
                      Q(customer__cellphone__icontains=q) |
                      Q(customer__phone__icontains=q)
                      ).distinct()
        date_range = request.GET.get('date_range', None)
        if date_range:
            date_range = date_range.split('-')
            date_range[0] = date_range[0].replace(' ', '')
            date_range[1] = date_range[1].replace(' ', '')
            try:
                date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
            except:
                date_start = datetime.datetime.now()
                date_end = datetime.datetime.now()
            qs = qs.filter(date__range=[date_start, date_end])
        return qs


@receiver(post_delete, sender=Order)
def update_costumer_order_value(sender, instance, **kwargs):
    customer = instance.customer
    customer.update_orders()


@receiver(post_delete, sender=Payment)
def update_costumer_payment_value(sender, instance, **kwargs):
    customer = instance.customer
    customer.update_payments()
