from django.urls import path
from .views import UserAPIView, UserExpensesAPIView, AddExpenseAPIView, OverallExpensesAPIView, DownloadBalanceSheetAPIView

urlpatterns = [
    path('users/', UserAPIView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserAPIView.as_view(), name='user-detail'),
    path('users/<int:user_id>/expenses/', UserExpensesAPIView.as_view(), name='user-expenses'),
    path('add-expense/', AddExpenseAPIView.as_view(), name='add-expense'),
    path('overall-expenses/', OverallExpensesAPIView.as_view(), name='overall-expenses'),
    path('download-balance-sheet/', DownloadBalanceSheetAPIView.as_view(), name='download-balance-sheet'),
]
