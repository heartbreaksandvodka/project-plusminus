import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SubscriptionPlan, Subscription, PaymentTransaction, PaystackWebhookLog
from .paystack_service import paystack_service
import hashlib
import hmac

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([])  # No authentication required
def subscription_plans_view(request):
    """Get all available subscription plans"""
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True)
        plans_data = []
        
        for plan in plans:
            plans_data.append({
                'id': str(plan.id),
                'name': plan.name,
                'plan_type': plan.plan_type,
                'description': plan.description,
                'price': str(plan.price),
                'currency': plan.currency,
                'duration_days': plan.duration_days,
                'max_algorithms': plan.max_algorithms,
                'max_mt5_accounts': plan.max_mt5_accounts,
                'features': plan.features
            })
        
        return Response({'plans': plans_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {e}")
        return Response(
            {'error': 'Failed to fetch subscription plans'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class SubscriptionPlansView(APIView):
    """Get all available subscription plans"""
    # No authentication required - users need to see plans before signing up
    
    def get(self, request):
        try:
            plans = SubscriptionPlan.objects.filter(is_active=True)
            plans_data = []
            
            for plan in plans:
                plans_data.append({
                    'id': str(plan.id),
                    'name': plan.name,
                    'plan_type': plan.plan_type,
                    'description': plan.description,
                    'price': str(plan.price),
                    'currency': plan.currency,
                    'duration_days': plan.duration_days,
                    'max_algorithms': plan.max_algorithms,
                    'max_mt5_accounts': plan.max_mt5_accounts,
                    'features': plan.features
                })
            
            return Response({'plans': plans_data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching subscription plans: {e}")
            return Response(
                {'error': 'Failed to fetch subscription plans'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InitializePaymentView(APIView):
    """Initialize a payment for subscription"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            plan_id = request.data.get('plan_id')
            callback_url = request.data.get('callback_url', 'http://localhost:3000/subscription/callback')
            
            if not plan_id:
                return Response(
                    {'error': 'plan_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the subscription plan
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {'error': 'Invalid subscription plan'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Initialize payment
            result = paystack_service.initialize_transaction(
                user=request.user,
                subscription_plan=plan,
                callback_url=callback_url
            )
            
            if result:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Failed to initialize payment'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error initializing payment: {e}")
            return Response(
                {'error': 'Failed to initialize payment'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([])  # No authentication required for payment verification
def verify_payment_view(request):
    """Verify a payment transaction - Public endpoint for payment redirects"""
    try:
        reference = request.data.get('reference')
        
        if not reference:
            return Response(
                {'error': 'reference is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Basic security: Check reference format (should start with expected prefix)
        if not reference.startswith(('test_', 'sub_', 'pay_')):
            return Response(
                {'error': 'Invalid reference format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rate limiting could be added here in production
        # Example: Check if same IP is making too many requests
        
        # Verify transaction with Paystack
        transaction_data = paystack_service.verify_transaction(reference)
        
        if not transaction_data:
            return Response(
                {'error': 'Transaction not found or verification failed'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if payment was successful
        if transaction_data.get('status') == 'success':
            # Return limited, safe information
            return Response({
                'status': 'success',
                'message': 'Payment verified successfully',
                'transaction': {
                    'reference': reference,
                    'amount': transaction_data.get('amount', 0) / 100,  # Convert from kobo
                    'currency': transaction_data.get('currency', 'ZAR'),
                    'status': transaction_data.get('status'),
                    'paid_at': transaction_data.get('paid_at', ''),
                    'channel': transaction_data.get('channel', ''),
                    # Note: We don't expose sensitive customer data like email without auth
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'failed',
                'message': 'Payment verification failed',
                'transaction_status': transaction_data.get('status', 'unknown')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return Response(
            {'error': 'Failed to verify payment'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class VerifyPaymentView(APIView):
    """Verify a payment transaction"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            reference = request.data.get('reference')
            
            if not reference:
                return Response(
                    {'error': 'reference is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify transaction
            transaction_data = paystack_service.verify_transaction(reference)
            
            if not transaction_data:
                return Response(
                    {'error': 'Failed to verify transaction'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Check if payment was successful
            if transaction_data.get('status') == 'success':
                # Process successful payment
                success = paystack_service.process_successful_payment(transaction_data)
                
                if success:
                    return Response({
                        'status': 'success',
                        'message': 'Payment verified and subscription activated',
                        'transaction': {
                            'reference': reference,
                            'amount': transaction_data.get('amount', 0) / 100,  # Convert from kobo
                            'currency': transaction_data.get('currency'),
                            'status': transaction_data.get('status')
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'error': 'Payment verified but failed to activate subscription'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response({
                    'status': 'failed',
                    'message': 'Payment was not successful',
                    'transaction_status': transaction_data.get('status')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return Response(
                {'error': 'Failed to verify payment'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSubscriptionView(APIView):
    """Get user's current subscription"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user's active subscription
            subscription = Subscription.objects.filter(
                user=request.user,
                status='active'
            ).first()
            
            if subscription:
                subscription_data = {
                    'id': str(subscription.id),
                    'plan': {
                        'id': str(subscription.plan.id),
                        'name': subscription.plan.name,
                        'plan_type': subscription.plan.plan_type,
                        'price': str(subscription.plan.price),
                        'currency': subscription.plan.currency,
                        'max_algorithms': subscription.plan.max_algorithms,
                        'max_mt5_accounts': subscription.plan.max_mt5_accounts,
                    },
                    'status': subscription.status,
                    'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
                    'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
                    'days_remaining': subscription.days_remaining,
                    'auto_renew': subscription.auto_renew,
                    'is_active': subscription.is_active
                }
                
                return Response({'subscription': subscription_data}, status=status.HTTP_200_OK)
            else:
                return Response({'subscription': None}, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error fetching user subscription: {e}")
            return Response(
                {'error': 'Failed to fetch subscription'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentHistoryView(APIView):
    """Get user's payment history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            history = paystack_service.get_payment_history(request.user)
            return Response({'transactions': history}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching payment history: {e}")
            return Response(
                {'error': 'Failed to fetch payment history'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@csrf_exempt
@require_http_methods(["POST"])
def paystack_webhook(request):
    """Handle Paystack webhook events"""
    try:
        # Verify webhook signature
        signature = request.headers.get('x-paystack-signature')
        
        if not signature:
            logger.warning("Webhook received without signature")
            return HttpResponse(status=400)
        
        # Verify the signature
        expected_signature = hmac.new(
            settings.PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
            request.body,
            hashlib.sha512
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid webhook signature")
            return HttpResponse(status=400)
        
        # Parse webhook data
        data = json.loads(request.body)
        event = data.get('event')
        
        # Log the webhook
        webhook_log = PaystackWebhookLog.objects.create(
            event=event,
            reference=data.get('data', {}).get('reference', ''),
            data=data
        )
        
        # Process specific events
        if event == 'charge.success':
            # Handle successful charge
            transaction_data = data['data']
            success = paystack_service.process_successful_payment(transaction_data)
            
            if success:
                webhook_log.processed = True
                webhook_log.save()
                logger.info(f"Successfully processed webhook for {transaction_data.get('reference')}")
            else:
                logger.error(f"Failed to process webhook for {transaction_data.get('reference')}")
        
        elif event == 'subscription.create':
            # Handle subscription creation
            logger.info(f"Subscription created: {data}")
        
        elif event == 'subscription.disable':
            # Handle subscription cancellation
            logger.info(f"Subscription disabled: {data}")
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return HttpResponse(status=500)
