from django.urls import path, include
from .views import test_get_view

app_name = 'incomes'

urlpatterns = [
    path('', test_get_view, name='home'),

]
