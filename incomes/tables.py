import django_tables2 as tables
from .models import Income


class IncomeTable(tables.Table):
    action = tables.TemplateColumn('''
                                     <div class="btn-group dropright">
                                        <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                        <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                            <span class="sr-only">Toggle Dropright</span>
                                        </button>
                                            <div class="dropdown-menu">
                                                <a class="dropdown-item" href="">---</a>    
                                            </div>
                                        </div>
                                        ''', verbose_name='Eπεξεργασια', orderable=False)

    class Meta:
        model = Income
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'sum_z', 'pos', 'order_cost', 'extra', 'logistic_value', 'value', 'action']