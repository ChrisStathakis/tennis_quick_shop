import django_tables2 as tables

from .models import Order, Payment


class OrderTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_costumer_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
        orderable=False,
    )
    tag_value = tables.Column(orderable=False, verbose_name='Αξία')

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'title', 'tag_value']


class PaymentTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_costumer_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
        orderable=False,
    )
    tag_value = tables.Column(orderable=False, verbose_name='Αξια')

    class Meta:
        model = Payment
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'title', 'tag_value']


class OrderTableListView(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
        orderable=False,
    )
    tag_value = tables.Column(orderable=False, verbose_name='Αξία')

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'customer', 'title', 'tag_value']


class PaymentTableListView(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
        orderable=False,
    )
    tag_value = tables.Column(orderable=False, verbose_name='Αξία')

    class Meta:
        model = Payment
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'customer', 'title', 'tag_value']
