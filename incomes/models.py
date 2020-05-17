from django.db import models
from django.shortcuts import reverse
from tinymce.models import HTMLField

from frontend.tools import initial_date

from django.conf import settings

CURRENCY = settings.CURRENCY


class Income(models.Model):
    date_expired = models.DateField(verbose_name='Ημερομηνια')
    sum_z = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Ζ Ημερας')
    pos = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Συνολο POS')
    order_cost = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Συνολο Τιμολογιων')
    extra = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Επιπλεον Εσοδα')
    notes = HTMLField(blank=True, null=True, verbose_name='Σημειωσεις')
    logistic_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Λογιστικο Συνολο')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Πραγματικο Συνολο')
    cash = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Μετρητα')

    class Meta:
        ordering = ['-date_expired']

    def __str__(self):
        return f'{self.date_expired}'

    def save(self, *args, **kwargs):
        self.logistic_value = self.sum_z + self.order_cost
        self.value = self.logistic_value + self.extra
        self.cash = self.sum_z - self.pos
        super().save(*args, **kwargs)

    def get_edit_url(self):
        return reverse('incomes:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('incomes:delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        search_name = request.GET.get('search_name', None)
        date_start, date_end, date_range = initial_date(request, 6)
        qs = qs.filter(notes__icontains=search_name) if search_name else qs
        if date_start and date_end:
            qs = qs.filter(date_expired__range=[date_start, date_end])
        return qs

    def tag_sum_z(self):
        return f'{self.sum_z} {CURRENCY}'

    def tag_pos(self):
        return f'{self.pos} {CURRENCY}'

    def tag_cash(self):
        return f'{self.cash} {CURRENCY}'

    def tag_order_cost(self):
        return f'{self.order_cost} {CURRENCY}'

    def tag_extra(self):
        return f'{self.extra} {CURRENCY}'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

