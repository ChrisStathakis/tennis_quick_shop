from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportModelAdmin
from .models import Product, Category, Vendor, ProductVendor
from .forms import VendorForm

from dal_admin_filters import AutocompleteFilter


def make_published(modeladmin, request, queryset):
    for ele in queryset:
        ele.save()

class CategoryFilter(AutocompleteFilter):
    title = 'Επιλογή Κατηγοριας'                    # filter's title
    field_name = 'categories'           # field name - ForeignKey to Country model
    autocomplete_url = 'category-autocomplete' # url name of Country autocomplete view


@admin.register(ProductVendor)
class ProductVendorAdmin(ImportExportModelAdmin):
    model = ProductVendor
    list_filter = [ 'vendor']
    list_display = ['id', '__str__']
    actions = [make_published, ]


class VendorInline(admin.TabularInline):
    model = ProductVendor
    form = VendorForm
    readonly_fields  = ['final_value']
    fields = ['product', 'vendor', 'sku', 'value', 'discount', 'final_value']


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    inlines = [VendorInline, ]
    search_fields = ['title', 'product_vendors__vendor__title']
    list_filter = ['active', 'categories', 'vendors']
    list_editable = ['qty',]
    filter_horizontal = ['categories']
    list_display_links = ['title']
    list_display = ['sku', 'title', 'qty', 'price_buy', 'value','tag_final_value']
    readonly_fields = ['tag_final_value']
    paginate_by = 30
    save_as = True
    fieldsets = (
        ('Στοιχεία Προϊόντος', {
            'description': "These fields are required for each event.",
             "fields": (('active', 'title'), ('sku', 'barcode'), ),
        }),
        (None, {
            "fields": (
                'categories',
            ),
        }),
        (None, {
            "fields": (
                'price_buy', 'value', 'value_discount', 'final_value'
            ),
        }),
    )

    class Media:
        pass

    
    
    

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, DraggableMPTTAdmin):
    search_fields = ['name', ]
