from django.db import models

from .models import Costumer


class PaymentInvoice(models.Model):
    SERIES = (
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'Γ')
    )
    number = models.IntegerField()
    series = models.CharField(max_length=1, choices=SERIES)
    place = models.CharField(max_length=220)
    date = models.DateField()

    clean_value = models.DecimalField(decimal_places=4, max_digits=17, default=0.00)
    taxes = models.DecimalField(decimal_places=4, max_digits=17, default=0.00)
    value = models.DecimalField(decimal_places=4, max_digits=17, default=0.00)
    taxes_modifier = models.IntegerField(default=24)

    class Meta:
        unique_together = ['number', 'series']

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_series_display()}-{self.number}'

    def tag_title(self):
        return f'{self.get_series_display()}-cs{self.number}'


class CostumerDetails(models.Model):
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT)
    invoice = models.ForeignKey(PaymentInvoice, on_delete=models.CASCADE)
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


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(PaymentInvoice, on_delete=models.CASCADE)
    UNITS = (
        ('a', 'Τεμάχιο'),
        ('b', 'Κιβώτιο'),
        ('c', 'Κιλό'),

    )
    title = models.CharField(max_length=250)
    unit = models.CharField(max_length=1, choices='', default='a')
    qty = models.DecimalField(max_digits=17, decimal_places=3, default=1)
    value = models.DecimalField(max_digits=17, decimal_places=3)
