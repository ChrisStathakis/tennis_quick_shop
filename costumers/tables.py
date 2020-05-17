import django_tables2 as tables

from .models import PaymentInvoice


class PaymentInvoiceTable(tables.Table):
    button = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' "
                                   "class='btn btn-info'><i class='fa fa-edit'></i></a>",
                                   orderable=False, verbose_name='Επιλογες'
                                   )

    tag_total_value = tables.Column(orderable=False, verbose_name='Τελικη Αξια')
    tag_title = tables.Column(orderable=False, verbose_name='Τιτλος')

    class Meta:
        model = PaymentInvoice
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'tag_title', 'order_type', 'costumer', 'tag_total_value', 'locked']

