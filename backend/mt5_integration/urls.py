from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.mt5_account, name='mt5_account'),
    path('test-connection/', views.test_mt5_connection, name='test_mt5_connection'),
    path('refresh-status/', views.refresh_account_status, name='refresh_account_status'),
    path('delete-account/', views.delete_mt5_account, name='delete_mt5_account'),
    path('algorithms/', views.algorithm_executions, name='algorithm_executions'),
    path('start-algorithm/', views.start_algorithm, name='start_algorithm'),
    path('stop-algorithm/<int:execution_id>/', views.stop_algorithm, name='stop_algorithm'),
]
