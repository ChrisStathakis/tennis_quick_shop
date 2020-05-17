import django_tables2 as tables

from .models import Payroll, Person, Occupation, BillCategory, Bill
from .calendar_model import PersonSchedule


class PersonScheduleTable(tables.Table):
    date_start = tables.TemplateColumn("<p>{{ record.date_start|date:'d-M-Y H:i'}} </p>")
    date_end = tables.TemplateColumn("<p>{{ record.date_end|date:'d-M-Y H:i'}} </p>")

    action = tables.TemplateColumn('''
                                         <div class="btn-group dropright">
                                            <a href='{{ record.get_delete_url }}' class="btn btn-danger"><i class='fa fa-remove'> </i></a>
                                            <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                                <span class="sr-only">Toggle Dropright</span>
                                            </button>
                                                <div class="dropdown-menu">
                                                    <a class="dropdown-item" href="{{ record.get_copy_url}}">Δημιουργια Αντιγραφου</a>
                                                </div>
                                            </div>
                                            ''', verbose_name='Eπεξεργασια', orderable=False)

    class Meta:
        model = PersonSchedule
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_start', 'date_end', 'hours', 'action']


class PayrollTable(tables.Table):
    checkbox_ = tables.TemplateColumn("<input name='invoice_name' value={{ record.id }} type='checkbox' class='form-control' /> ",
                                      orderable=False, verbose_name='Επιλογή')
    action = tables.TemplateColumn('''
                                     <div class="btn-group dropright">
                                        <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                        <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                            <span class="sr-only">Toggle Dropright</span>
                                        </button>
                                            <div class="dropdown-menu">
                                                <a class="dropdown-item" href="{{ record.get_copy_url}}">Δημιουργια Αντιγραφου</a>
                                                 <a class="dropdown-item" href="{{ record.get_pay_url}}">Πληρωμη/Αποπληρωμη</a>     
                                            </div>
                                        </div>
                                        ''', verbose_name='Eπεξεργασια', orderable=False)
    tag_final_value = tables.Column('Aξια', orderable=False)
    date_expired = tables.TemplateColumn("<p>{{ record.date_expired|date:'d/M/Y'}} </p>")

    class Meta:
        model = Payroll
        template_name = 'django_tables2/bootstrap.html'
        fields = ['checkbox_', 'date_expired', 'person', 'category', 'tag_final_value', 'is_paid', 'action']


class PayrollCardTable(tables.Table):
    action = tables.TemplateColumn('''
                                     <div class="btn-group dropright">
                                        <a href='{{ record.get_edit_card_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                        <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                            <span class="sr-only">Toggle Dropright</span>
                                        </button>
                                            <div class="dropdown-menu">
                                                <a class="dropdown-item" href="{{ record.get_copy_url}}">Δημιουργια Αντιγραφου</a>
                                                 <a class="dropdown-item" href="{{ record.get_pay_url}}">Πληρωμη/Αποπληρωμη</a>     
                                            </div>
                                        </div>
                                        ''', verbose_name='Eπεξεργασια', orderable=False)
    tag_final_value = tables.Column('Aξια', orderable=False)

    class Meta:
        model = Payroll
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'category', 'tag_final_value', 'is_paid', 'action']


class PersonTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-info'>"
                                   "<i class='fa fa-edit'> </i> </a>", orderable=False, verbose_name='Επεξεργασια')
    
    card = tables.TemplateColumn("<a href='{{ record.get_card_url }}' class='btn btn-primary'>"
                                   "<i class='fa fa-eye'> </i> </a>", orderable=False, verbose_name='Καρτελα')

    tag_balance = tables.Column(verbose_name='Υπόλοιπο', orderable=False)

    class Meta:
        model = Person
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'phone', 'occupation', 'tag_balance', 'card', 'action']


class OccupationTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-info'>"
                                   "<i class='fa fa-edit'> </i> </a>", orderable=False, verbose_name='Επεξεργασια')

    class Meta:
        model = Occupation
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'active', 'action']


class BillTable(tables.Table):
    action = tables.TemplateColumn('''
                                         <div class="btn-group dropright">
                                            <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                            <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                                <span class="sr-only">Toggle Dropright</span>
                                            </button>
                                                <div class="dropdown-menu">
                                                    <a class="dropdown-item" href="{{ record.get_copy_url}}">Δημιουργια Αντιγραφου</a>
                                                     <a class="dropdown-item" href="{{ record.get_pay_url}}">Πληρωμη/Αποπληρωμη</a>     
                                                </div>
                                            </div>
                                            ''', verbose_name='Eπεξεργασια', orderable=False)

    tag_final_value = tables.Column(orderable=False, verbose_name='Αξια')

    class Meta:
        model = Bill
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'category', 'payment_method', 'tag_final_value', 'is_paid', 'action']


class BillFromCategoryTable(BillTable):
    action = tables.TemplateColumn('''
                                     <div class="btn-group dropright">
                                        <button data-href='{{ record.get_modal_url }}' class="btn btn-secondary edit_button"><i class='fa fa-edit edit_button'> </i></button>
                                        <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                            <span class="sr-only">Toggle Dropright</span>
                                        </button>
                                            <div class="dropdown-menu">
                                                <a class="dropdown-item" href="{{ record.get_copy_url}}">Δημιουργια Αντιγραφου</a>
                                                <a class="dropdown-item" href="{{ record.get_pay_url}}">Πληρωμη/Αποπληρωμη</a>
                                                  
                                            </div>
                                        </div>
                                        ''', orderable=False, verbose_name='Επεξεργασια')

    class Meta:
        template_name = 'django_tables2/bootstrap.html'


class BillCategoryTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>"
                                   "<i class='fa fa-edit'> </i> </a>",
                                   orderable=False, verbose_name='Επεξεργασια')

    card = tables.TemplateColumn("<a href='{{ record.get_card_url }}' class='btn btn-info btn-round'>"
                                   "<i class='fa fa-eye'> </i> </a>",
                                 orderable=False, verbose_name='Καρτελα')
    tag_balance = tables.Column(orderable=False, verbose_name='Υπολοιπο')

    class Meta:
        model = BillCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'tag_balance', 'active', 'action']
