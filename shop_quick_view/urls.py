from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('costumers/', include('costumers.urls')),
    path('', include('frontend.urls')),
    path('warehouse/', include('vendors.urls')),
    path('products/', include('products.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('payrolls-and-bills/', include('payroll.urls')),
    path('incomes/', include('incomes.urls')),
    path('analysis/', include('analysis.urls')),
    path('generic-expenses/', include('general_expenses.urls')),
    path('notebook/', include('notebook.urls')),

    path('myData/', include('myData.urls'))
]
