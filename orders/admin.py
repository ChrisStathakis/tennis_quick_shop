from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Payment, Order


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    pass