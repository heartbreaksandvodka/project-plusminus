import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from pypaystack2 import PaystackClient
from .models import PaymentTransaction, Subscription, SubscriptionPlan
import uuid

User = get_user_model()
logger = logging.getLogger(__name__)


class PaystackService:
    """Service class for handling Paystack payments"""
    
    def __init__(self):
        if not settings.PAYSTACK_SECRET_KEY:
            raise ValueError("PAYSTACK_SECRET_KEY is required in settings")
        
        self.paystack = PaystackClient(secret_key=settings.PAYSTACK_SECRET_KEY)
    
    def create_customer(self, user) -> Optional[str]:
        """Create a customer on Paystack"""
        try:
            response = self.paystack.customers.create(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=getattr(user, 'phone', '')
            )
            
            if response.status_code == 200 and response.data:
                customer_code = response.data.customer_code
                logger.info(f"Created Paystack customer {customer_code} for user {user.email}")
                return customer_code
            else:
                logger.error(f"Failed to create Paystack customer: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None
    
    def initialize_transaction(self, user, subscription_plan, 
                             callback_url: str = None) -> Optional[Dict[str, Any]]:
        """Initialize a payment transaction"""
        try:
            # Generate unique reference
            reference = f"sub_{uuid.uuid4().hex[:12]}"
            
            # Convert amount to kobo (Paystack expects amount in kobo for ZAR)
            amount_kobo = int(subscription_plan.price * 100)
            
            # Create transaction record
            transaction = PaymentTransaction.objects.create(
                user=user,
                transaction_type='subscription',
                amount=subscription_plan.price,
                currency=subscription_plan.currency,
                paystack_reference=reference,
                metadata={
                    'plan_id': str(subscription_plan.id),
                    'plan_name': subscription_plan.name,
                    'user_id': str(user.id)
                }
            )
            
            # Initialize transaction with Paystack
            response = self.paystack.transactions.initialize(
                email=user.email,
                amount=amount_kobo,
                currency=subscription_plan.currency,
                reference=reference,
                callback_url=callback_url,
                metadata={
                    'transaction_id': str(transaction.id),
                    'plan_id': str(subscription_plan.id),
                    'user_id': str(user.id)
                }
            )
            
            if response.status_code == 200 and response.data:
                # Update transaction with Paystack response
                transaction.gateway_response = response.data.__dict__
                transaction.status = 'processing'
                transaction.save()
                
                logger.info(f"Initialized transaction {reference} for user {user.email}")
                
                return {
                    'status': True,
                    'transaction_id': str(transaction.id),
                    'reference': reference,
                    'authorization_url': response.data.authorization_url,
                    'access_code': response.data.access_code
                }
            else:
                transaction.status = 'failed'
                transaction.gateway_response = {'error': 'Failed to initialize'}
                transaction.save()
                logger.error(f"Failed to initialize transaction: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error initializing transaction: {e}")
            return None
    
    def verify_transaction(self, reference: str) -> Optional[Dict[str, Any]]:
        """Verify a payment transaction"""
        try:
            response = self.paystack.transactions.verify(reference=reference)
            
            if response.status_code == 200 and response.data:
                transaction_data = response.data.__dict__
                logger.info(f"Verified transaction {reference}: {transaction_data.get('status')}")
                return transaction_data
            else:
                logger.error(f"Failed to verify transaction {reference}: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error verifying transaction: {e}")
            return None
    
    def process_successful_payment(self, transaction_data: Dict[str, Any]) -> bool:
        """Process a successful payment and activate subscription"""
        try:
            reference = transaction_data.get('reference')
            
            # Get the transaction record
            transaction = PaymentTransaction.objects.get(paystack_reference=reference)
            
            # Update transaction status
            transaction.status = 'success'
            transaction.paystack_transaction_id = str(transaction_data.get('id', ''))
            transaction.paystack_authorization_code = transaction_data.get('authorization', {}).get('authorization_code', '')
            transaction.payment_method = transaction_data.get('channel', '')
            transaction.gateway_response = transaction_data
            transaction.completed_at = timezone.now()
            transaction.save()
            
            # Get the subscription plan
            plan_id = transaction.metadata.get('plan_id')
            plan = SubscriptionPlan.objects.get(id=plan_id)
            
            # Create or update subscription
            subscription, created = Subscription.objects.get_or_create(
                user=transaction.user,
                plan=plan,
                defaults={
                    'status': 'active',
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timezone.timedelta(days=plan.duration_days)
                }
            )
            
            if not created:
                # Update existing subscription
                subscription.status = 'active'
                subscription.start_date = timezone.now()
                subscription.end_date = timezone.now() + timezone.timedelta(days=plan.duration_days)
                subscription.save()
            
            # Link transaction to subscription
            transaction.subscription = subscription
            transaction.save()
            
            logger.info(f"Successfully processed payment for user {transaction.user.email}")
            return True
            
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Transaction not found for reference {reference}")
            return False
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
            return False
    
    def create_subscription_plan(self, plan) -> Optional[str]:
        """Create a subscription plan on Paystack"""
        try:
            # Convert amount to kobo
            amount_kobo = int(plan.price * 100)
            
            # Create plan on Paystack
            response = self.paystack.plans.create(
                name=plan.name,
                amount=amount_kobo,
                interval='monthly' if plan.duration_days == 30 else 'annually',
                currency=plan.currency,
                description=plan.description
            )
            
            if response.status_code == 200 and response.data:
                plan_code = response.data.plan_code
                logger.info(f"Created Paystack plan {plan_code} for {plan.name}")
                return plan_code
            else:
                logger.error(f"Failed to create Paystack plan: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return None
    
    def get_payment_history(self, user) -> list:
        """Get payment history for a user"""
        try:
            transactions = PaymentTransaction.objects.filter(user=user).order_by('-created_at')
            
            history = []
            for transaction in transactions:
                history.append({
                    'id': str(transaction.id),
                    'amount': str(transaction.amount),
                    'currency': transaction.currency,
                    'status': transaction.status,
                    'transaction_type': transaction.transaction_type,
                    'reference': transaction.paystack_reference,
                    'created_at': transaction.created_at.isoformat(),
                    'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return []


# Create a singleton instance
paystack_service = PaystackService()
