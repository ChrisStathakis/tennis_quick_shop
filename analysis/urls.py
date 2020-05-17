from django.urls import path

from .views import AnalysisHomepage, AnalysisIncomeView, AnalysisOutcomeView, CashRowView, BalanceSheetView, StoreInventoryView

app_name='analysis'

urlpatterns = [
    path('homepage/', AnalysisHomepage.as_view(), name='homepage'),
    path('incomes/', AnalysisIncomeView.as_view(), name='income_analysis'),
    path('outcomes/', AnalysisOutcomeView.as_view(), name='outcome_analysis'),
    path('cash-row/', CashRowView.as_view(), name='cash_row'),
    path('balance-sheet/', BalanceSheetView.as_view(), name='balance_sheet'),
    path('apografi/', StoreInventoryView.as_view(), name='store_inventory')
    
]