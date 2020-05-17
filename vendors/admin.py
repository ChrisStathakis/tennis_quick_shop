from django.contrib import admin
from .models import Vendor, Employer, Invoice, Payment
from import_export.admin import ImportExportModelAdmin
from products.models import ProductVendor
from products.forms import ProductForm


def update_vendor_taxes(modeladmin, request, queryset):
    queryset.update(taxes_modifier='c')


class VendorProductInline(admin.TabularInline):
    model = ProductVendor
    form = ProductForm
    fields = ['product', 'vendor', 'sku', 'value', 'discount', 'final_value']

    
@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin):
    list_display = ['title', 'phone', 'email', 'tag_balance', 'active']
    list_filter = ['active']
    search_fields = ['title', 'phone', 'afm', 'cellphone', ]
    readonly_fields = ['tag_balance']
    inlines = [VendorProductInline, ]
    ordering = ['title']
    actions = [update_vendor_taxes, ]
    fieldsets = (
          ('Βασικά Στοιχεία', {
              'description': "These fields are required for each event.",
              'fields': ('active', 
                      ('title','owner'),
                      ('cellphone', 'phone') 
                       )
         }),
         ('Πληροφοριες', {
              'classes': ('collapse',),
              'description': "Email, Site, διευθύνσεις",
              'fields': (('email', 'site'), 
                         ('address', 'city'),
                          'description'
                       
                       )
         }),
         ('Πληροφοριες Εφοριας', {
             'classes': ('collapse',),
             'fields': ('afm', 'doy', 'taxes_modifier')
         }),
     )

   

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['date', 'title', 'vendor', 'value']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['date', 'title', 'vendor', 'value']