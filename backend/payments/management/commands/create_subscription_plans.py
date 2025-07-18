from django.core.management.base import BaseCommand
from payments.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create initial subscription plans for the trading platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating subscription plans...'))

        plans_data = [
            {
                'name': 'Basic Trader',
                'plan_type': 'basic',
                'description': 'Perfect for beginners getting started with algorithmic trading',
                'price': 299.00,
                'duration_days': 30,
                'max_algorithms': 2,
                'max_mt5_accounts': 1,
                'features': [
                    'Access to 2 basic trading algorithms',
                    '1 MT5 account connection',
                    'Basic market analysis tools',
                    'Email support',
                    'Trading performance reports'
                ]
            },
            {
                'name': 'Premium Trader',
                'plan_type': 'premium',
                'description': 'For serious traders who want more algorithms and features',
                'price': 599.00,
                'duration_days': 30,
                'max_algorithms': 5,
                'max_mt5_accounts': 2,
                'features': [
                    'Access to 5 advanced trading algorithms',
                    '2 MT5 account connections',
                    'Advanced market analysis tools',
                    'Risk management tools',
                    'Real-time notifications',
                    'Priority email support',
                    'Detailed trading analytics'
                ]
            },
            {
                'name': 'Professional Trader',
                'plan_type': 'pro',
                'description': 'For professional traders and small firms',
                'price': 1199.00,
                'duration_days': 30,
                'max_algorithms': 10,
                'max_mt5_accounts': 5,
                'features': [
                    'Access to 10 professional trading algorithms',
                    '5 MT5 account connections',
                    'Advanced portfolio management',
                    'Custom algorithm parameters',
                    'Advanced risk management',
                    'Real-time alerts and notifications',
                    'Priority phone and email support',
                    'Advanced reporting and analytics',
                    'Algorithm performance optimization'
                ]
            },
            {
                'name': 'Enterprise Solution',
                'plan_type': 'enterprise',
                'description': 'For large trading firms and institutional clients',
                'price': 2499.00,
                'duration_days': 30,
                'max_algorithms': -1,  # Unlimited
                'max_mt5_accounts': 20,
                'features': [
                    'Unlimited access to all trading algorithms',
                    'Up to 20 MT5 account connections',
                    'Custom algorithm development',
                    'Dedicated account manager',
                    'Advanced portfolio management',
                    'Custom risk management rules',
                    'Real-time monitoring dashboard',
                    '24/7 phone and email support',
                    'Custom reporting and analytics',
                    'API access for custom integrations',
                    'White-label solutions available'
                ]
            }
        ]

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name} - R{plan.price}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created/verified all subscription plans!')
        )
