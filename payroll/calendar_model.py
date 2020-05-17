from django.db import models
from django.shortcuts import reverse
from .models import Person

from frontend.tools import initial_date

class PersonSchedule(models.Model):
    date_start = models.DateTimeField(verbose_name='Απο')
    date_end = models.DateTimeField(verbose_name='Μεχρι')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='schedules')
    hours = models.DecimalField(default=0, decimal_places=2, max_digits=10)

    class Meta:
        ordering = ['-date_start']

    def save(self, *args, **kwargs):
        diff = self.date_end - self.date_start
        days, seconds = diff.days, diff.seconds
        self.hours = days * 24 + seconds // 3600
        super().save(*args, **kwargs)

    def get_delete_url(self):
        return reverse('payroll_bills:delete_schedule', kwargs={'pk': self.id})

    def get_copy_url(self):
        return reverse('payroll_bills:copy_schedule', kwargs={'pk': self.id})

    @property
    def date(self):
        return self.date_start.date()

    def type_of(self):
        return 'hour'

    @staticmethod
    def filters_data(request, queryset):
        person_name = request.GET.getlist('person_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        occup_name = request.GET.getlist('cate_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        date_start, date_end, date_range = initial_date(request, 6)
        queryset = queryset.filter(date_start__date__range=[date_start, date_end]) if date_start and date_end else queryset
        queryset = queryset.filter(is_paid=True) if 'paid' in paid_name else queryset.filter(is_paid=False) \
            if 'not_' in paid_name else queryset
        queryset = queryset.filter(category__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(person__id__in=person_name) if person_name else queryset
        queryset = queryset.filter(person__occupation__id__in=occup_name) if occup_name else queryset


        return queryset
