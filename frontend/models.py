from django.db import models
from django.urls import reverse
# Create your models here.

PAYMENT_METHOD_CATEGORY = (
    ('a', 'Αντικαταβολή'),
    ('b', 'Τραπεζική ΚατάΘεση')
)


class PaymentMethod(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name='Ονομασια')
    category = models.CharField(max_length=1, choices=PAYMENT_METHOD_CATEGORY, verbose_name='Κατηγορια')

    def __str__(self):
        return self.title

    @staticmethod
    def filters_data(request, qs):

        return qs

    def get_edit_url(self):
        return reverse('payment_method_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('payment_method_delete', kwargs={'pk': self.pk})
