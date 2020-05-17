import django_tables2 as tables

from costumers.models import Costumer, PaymentMethod


class CostumerTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
        orderable=False, verbose_name='Καρτέλα'
        )
    quick_view = tables.TemplateColumn(
        "<a data-href='{{ record.get_quick_view_url }}' class='btn btn-success btn-round quick_view'><i class='fa fa-eye'></i></a>",
        orderable=False, verbose_name='Πληρωμη'
        )

    actions = tables.TemplateColumn(
        '<a href="{{ record.get_order_url }}" class="btn btn-warning btn-round">'
        '<i class="fa fa-plus"> Παραστατικο</i>'
        '</a>'
        , orderable=False, verbose_name='Δημιουργια'
    )

    tag_balance = tables.Column(orderable=False, verbose_name='Υπολοιπο')

    class Meta:
        model = Costumer
        template_name = 'django_tables2/bootstrap.html'
        fields = ['eponimia', 'amka', 'afm', 'tag_balance', 'actions', 'action']


class PaymentMethodTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
        orderable=False, verbose_name='-'
    )

    class Meta:
        model = PaymentMethod
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'action']