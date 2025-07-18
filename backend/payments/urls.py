from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Subscription plans
    path('plans/', views.subscription_plans_view, name='subscription_plans'),
    
    # Payment flows (public verification for redirects)
    path('verify/', views.verify_payment_view, name='verify_payment_public'),
    path('verify-auth/', views.VerifyPaymentView.as_view(), name='verify_payment_auth'),
    path('initialize/', views.InitializePaymentView.as_view(), name='initialize_payment'),
    
    # User subscription and history
    path('subscription/', views.UserSubscriptionView.as_view(), name='user_subscription'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    
    # Webhooks
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]
