from django.urls import path
from . import views

app_name = "common"

urlpatterns = [
    path('accounts/', views.get_all_accounts, name='get_all_accounts'),
    path('accounts/<int:account_id>/', views.get_account_by_id, name='get_account_by_id'),
    path('accounts/create/', views.create_account, name='create_account'),
    path('accounts/update/<int:account_id>/', views.update_account, name='update_account'),
    path('accounts/delete/<int:account_id>/', views.delete_account, name='delete_account'),
]