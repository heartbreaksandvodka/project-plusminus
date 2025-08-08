from django.urls import path

from .api_views.mt5_authentication_views import mt5_account
from .api_views.mt5_verification_views import test_mt5_connection, refresh_account_status
from .api_views.user_mt5_views import delete_mt5_account
from .api_views.ea_trading_views import algorithm_executions
from .api_views.trade_execution_views import start_algorithm, stop_algorithm, pause_algorithm, resume_algorithm
from .api_views.account_status_views import account_statistics
from .api_views.manual_trading_views import manual_statistics

urlpatterns = [
    path('account/', mt5_account, name='mt5_account'),
    path('test-connection/', test_mt5_connection, name='test_mt5_connection'),
    path('refresh-status/', refresh_account_status, name='refresh_account_status'),
    path('delete-account/', delete_mt5_account, name='delete_mt5_account'),
    path('algorithms/', algorithm_executions, name='algorithm_executions'),
    path('start-algorithm/', start_algorithm, name='start_algorithm'),
    path('stop-algorithm/<int:execution_id>/', stop_algorithm, name='stop_algorithm'),
    path('pause-algorithm/<int:execution_id>/', pause_algorithm, name='pause_algorithm'),
    path('resume-algorithm/<int:execution_id>/', resume_algorithm, name='resume_algorithm'),
    path('account-statistics/', account_statistics, name='account_statistics'),
    path('manual-statistics/', manual_statistics, name='manual_statistics'),
]
