from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import PaymentInvoice, MyCard
from orders.models import Order, Costumer
from .tables import PaymentInvoiceTable
from .forms import PaymentInvoiceForm, CostumerDetailsForm, CreateInvoiceItemForm, PaymentInvoiceEditForm

from reportlab.pdfgen import canvas
import io
from django.http import FileResponse


@method_decorator(staff_member_required, name='dispatch')
class PaymentInvoiceListView(ListView):
    template_name = 'list_view.html'
    model = PaymentInvoice

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queryset_table'] = PaymentInvoiceTable(self.object_list)
        context['create_url'] = reverse('costumers:check_if_locked')
        context['back_url'] = reverse('costumer_homepage')
        return context


@staff_member_required
def check_if_locked_view(request):
    qs = PaymentInvoice.objects.filter(locked=False)
    if qs.exists():
        messages.warning(request, 'Πρεπει πρωτα να κλειδωσετε τα παραστατικα')
        return redirect(reverse('costumers:home'))
    else:
        return redirect(reverse('costumers:payment_invoice_create'))


@method_decorator(staff_member_required, name='dispatch')
class PaymentInvoiceCreateView(CreateView):
    template_name = 'form_view.html'
    model = PaymentInvoice
    form_class = PaymentInvoiceForm

    def get_initial(self):
        initial = super().get_initial()
        fav_card = MyCard.objects.filter(favorite=True)
        if fav_card.exists():
            initial['card_info'] = fav_card.first()
        return initial

    def get_success_url(self):
        return self.new_instance.get_edit_url()

    def form_valid(self, form):
        self.new_instance = form.save()
        return super(PaymentInvoiceCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Δημιουργια Παραστατικου'
        context['back_url'] = reverse('costumers:home')

        return context


@method_decorator(staff_member_required, name='dispatch')
class PaymentInvoiceCreateFromOrderView(CreateView):
    template_name = 'form_view.html'
    model = PaymentInvoice
    form_class = PaymentInvoiceForm

    def get_initial(self):
        costumer = get_object_or_404(Costumer, id=self.kwargs['pk'])
        initial = super().get_initial()
        fav_card = MyCard.objects.filter(favorite=True)
        if fav_card.exists():
            initial['card_info'] = fav_card.first()
        initial['costumer'] = costumer
        return initial

    def get_success_url(self):
        return self.new_instance.get_edit_url()

    def form_valid(self, form):
        self.new_instance = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Δημιουργια Παραστατικου'
        context['back_url'] = reverse('costumers:home')

        return context


@method_decorator(staff_member_required, name='dispatch')
class PaymentInvoiceUpdateView(UpdateView):
    template_name = 'costumers/update_invoice.html'
    model = PaymentInvoice
    form_class = PaymentInvoiceEditForm

    def get_success_url(self):
        return self.object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['costumer_form'] = CostumerDetailsForm(self.request.POST or None, instance=self.object.profile)
        context['item_form'] = CreateInvoiceItemForm(self.request.POST or None, initial={'invoice': self.object})
        qs = Order.objects.filter(favorite=True)
        context['order'] = qs.first() if qs.exists() else None
        return context

    def form_valid(self, form):
        form.save()
        return super(PaymentInvoiceUpdateView, self).form_valid(form)


@staff_member_required()
def print_invoice_view(request, pk):
    instance = get_object_or_404(PaymentInvoice, id=pk)
    costumer = instance.profile
    card = instance.card_info
    return render(request, 'costumers/print/index.html', {'instance': instance,
                                                          'costumer': costumer,
                                                          'card_info': card
                                                          })


@staff_member_required
def locked_invoice_view(request, pk):
    instance = get_object_or_404(PaymentInvoice, id=pk)
    instance.locked = True
    instance.save()
    return redirect(instance.get_edit_url())


@staff_member_required
def delete_payment_invoice(request, pk):
    instance = get_object_or_404(PaymentInvoice, id=pk)
    if instance.locked:
        messages.warning(request, 'Δε μπορει να διαγραφει αυτο το παραστατικο')
    else:
        instance.delete()
        messages.success(request, 'Το Παραστατικο Διαγραφηκε')
    return redirect('costumers:home')


def test_pdf(request):
    buffer = io.BytesIO()
    # Creating Canvas
    c = canvas.Canvas(buffer, pagesize=(200, 250), bottomup=0)
    # Logo Section
    # Setting th origin to (10,40)
    c.translate(10, 40)
    # Inverting the scale for getting mirror Image of logo
    c.scale(1, -1)
    # Inserting Logo into the Canvas at required position
    c.drawImage("logo.jpg", 0, 0, width=50, height=30)
    # Title Section
    # Again Inverting Scale For strings insertion
    c.scale(1, -1)
    # Again Setting the origin back to (0,0) of top-left
    c.translate(-10, -40)
    # Setting the font for Name title of company
    c.setFont("Helvetica-Bold", 10)
    # Inserting the name of the company
    c.drawCentredString(125, 20, "XYZ PRIVATE LIMITED")
    # For under lining the title
    c.line(70, 22, 180, 22)
    # Changing the font size for Specifying Address
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(125, 30, "Block No. 101, Triveni Apartments, Pitam Pura,")
    c.drawCentredString(125, 35, "New Delhi - 110034, India")
    # Changing the font size for Specifying GST Number of firm
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(125, 42, "GSTIN : 07AABCS1429B1Z")
    # Line Seprating the page header from the body
    c.line(5, 45, 195, 45)
    # Document Information
    # Changing the font for Document title
    c.setFont("Courier-Bold", 8)
    c.drawCentredString(100, 55, "TAX-INVOICE")
    # This Block Consist of Costumer Details
    c.roundRect(15, 63, 170, 40, 10, stroke=1, fill=0)
    c.setFont("Times-Bold", 5)
    c.drawRightString(70, 70, "INVOICE No. :")
    c.drawRightString(70, 80, "DATE :")
    c.drawRightString(70, 90, "CUSTOMER NAME :")
    c.drawRightString(70, 100, "PHONE No. :")
    # This Block Consist of Item Description
    c.roundRect(15, 108, 170, 130, 10, stroke=1, fill=0)
    c.line(15, 120, 185, 120)
    c.drawCentredString(25, 118, "SR No.")
    c.drawCentredString(75, 118, "GOODS DESCRIPTION")
    c.drawCentredString(125, 118, "RATE")
    c.drawCentredString(148, 118, "QTY")
    c.drawCentredString(173, 118, "TOTAL")
    # Drawing table for Item Description
    c.line(15, 210, 185, 210)
    c.line(35, 108, 35, 220)
    c.line(115, 108, 115, 220)
    c.line(135, 108, 135, 220)
    c.line(160, 108, 160, 220)
    # Declaration and Signature
    c.line(15, 220, 185, 220)
    c.line(100, 220, 100, 238)
    c.drawString(20, 225, "We declare that above mentioned")
    c.drawString(20, 230, "information is true.")
    c.drawString(20, 235, "(This is system generated invoive)")
    c.drawRightString(180, 235, "Authorised Signatory")
    # End the Page and Start with new
    c.showPage()
    # Saving the PDF
    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')



