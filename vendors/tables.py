import django_tables2 as tables

from .models import Invoice, Payment, Vendor
from products.models import Product


class ProductVendorTable(tables.Table):
    action = tables.TemplateColumn(
                '''
                                <div class="btn-group dropright">
                                            <button data-href='{% url 'vendors:ajax_product_modal_quick_view' record.id %}' class='btn btn-success quick_view_'><i class='fa fa-print'> </i> </button>
                                            <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                                <span class="sr-only">Toggle Dropright</span>
                                            </button>
                                                <div class="dropdown-menu">
                                                     <a target="_blank" class="dropdown-item" href="{% url 'vendors:copy_product_from_vendor' record.id vendor.id %}">Προσθηκη Προμηθευτή</a>     
                                                </div>
                                            </div>
                                ''', verbose_name='Eπεξεργασια', orderable=False)
    # action = tables.TemplateColumn("<button data-href='{% url 'vendors:ajax_product_modal_quick_view' record.id %}' class='btn btn-success quick_view_'><i class='fa fa-print'> </i> </button>")
    tag_price_buy = tables.Column(verbose_name='Αξια Αποθηκης', orderable=False)
    tag_final_value = tables.Column(verbose_name='Αξια Πωλησης', orderable=False)
    qty = tables.Column(verbose_name='Ποσοτητα', orderable=False)
    title = tables.Column(verbose_name='ΠροΪον', orderable=False)

    class Meta:
        model = Product
        template_name = 'django_tables2/bootstrap.html'
        fields = ['sku', 'title', 'tag_price_buy', 'qty', 'tag_final_value', 'action']


class VendorTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url}}' class='btn btn-warning'><span class='fa fa-edit'></span></a>", 
            orderable=False, verbose_name='-')
    tag_balance = tables.Column(orderable=False, verbose_name='Υπολοιπο')
    title =  tables.TemplateColumn("<a href='{{ record.get_edit_url}}'>{{ record }}</a>", 
            orderable=False, verbose_name='-')

    class Meta:
        model = Vendor
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'afm', 'phone',  'email', 'tag_balance']





    