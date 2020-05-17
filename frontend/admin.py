from django.contrib import admin

from  frontend.models import PaymentMethod, PAYMENT_METHOD_CATEGORY


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass



