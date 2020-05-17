import django_tables2 as tables

from .models import GeneralExpenseCategory, GeneralExpense


class GeneralExpenseTable(tables.Table):
    action = tables.TemplateColumn('''
                                         <div class="btn-group dropright">
                                            <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                            <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                                <span class="sr-only">Toggle Dropright</span>
                                            </button>
                                                <div class="dropdown-menu">
                                                    
                                                     <a class="dropdown-item" href="{{ record.get_pay_url}}">Πληρωμη/Αποπληρωμη</a>     
                                                </div>
                                            </div>
                                            ''', verbose_name='Eπεξεργασια', orderable=False)
    tag_value = tables.Column(orderable=False, verbose_name='Αξια')

    class Meta:
        model = GeneralExpense
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'title', 'category', 'is_paid', 'tag_value']


class GeneralExpenseCategoryTable(tables.Table):
    action = tables.TemplateColumn('''
                                    <div class="btn-group dropright">
                                        <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>  
                                    </div>
                                    ''', verbose_name='Eπεξεργασια', orderable=False)

    class Meta:
        model = GeneralExpenseCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title']