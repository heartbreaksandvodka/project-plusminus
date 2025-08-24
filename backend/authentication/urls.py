from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import ea_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('settings/', views.user_settings, name='user_settings'),
    
    # EA Token Management Endpoints
    path('ea-tokens/', ea_views.list_ea_tokens, name='list_ea_tokens'),
    path('ea-tokens/create/', ea_views.create_ea_token, name='create_ea_token'),
    path('ea-tokens/<int:token_id>/update/', ea_views.update_ea_token, name='update_ea_token'),
    path('ea-tokens/<int:token_id>/revoke/', ea_views.revoke_ea_token, name='revoke_ea_token'),
    path('ea-tokens/<int:token_id>/regenerate/', ea_views.regenerate_ea_token, name='regenerate_ea_token'),
    path('ea-tokens/<int:token_id>/logs/', ea_views.ea_connection_logs, name='ea_connection_logs'),
]
