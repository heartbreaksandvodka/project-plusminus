import api from './client';

export interface UserSubscription {
  id: number;
  plan_type: 'basic' | 'premium' | 'pro' | 'enterprise';
  max_algorithms: number;
  max_mt5_accounts: number;
  status: 'active' | 'inactive' | 'cancelled' | 'expired';
  start_date: string;
  end_date?: string;
  auto_renew: boolean;
  features: string[];
}

export interface SubscriptionPlan {
  id: number;
  name: string;
  plan_type: string;
  price_monthly: number;
  price_yearly: number;
  max_algorithms: number;
  max_mt5_accounts: number;
  features: string[];
  is_popular: boolean;
}

export const subscriptionsService = {
  // Get user's current subscription
  getUserSubscription: async (): Promise<UserSubscription> => {
    const response = await api.get('/subscriptions/current/');
    return response.data;
  },

  // Get available subscription plans
  getPlans: async (): Promise<SubscriptionPlan[]> => {
    const response = await api.get('/subscriptions/plans/');
    return response.data;
  },

  // Subscribe to a plan
  subscribe: async (planId: number, paymentMethodId: string): Promise<any> => {
    const response = await api.post('/subscriptions/subscribe/', {
      plan_id: planId,
      payment_method_id: paymentMethodId
    });
    return response.data;
  },

  // Cancel subscription
  cancelSubscription: async (): Promise<any> => {
    const response = await api.post('/subscriptions/cancel/');
    return response.data;
  },

  // Update subscription
  updateSubscription: async (planId: number): Promise<any> => {
    const response = await api.post('/subscriptions/update/', {
      plan_id: planId
    });
    return response.data;
  },

  // Get subscription usage
  getUsage: async (): Promise<any> => {
    const response = await api.get('/subscriptions/usage/');
    return response.data;
  },
};

// Export individual functions for convenience
export const getUserSubscription = subscriptionsService.getUserSubscription;
export const getSubscriptionPlans = subscriptionsService.getPlans;
export const subscribeToplan = subscriptionsService.subscribe;

export default subscriptionsService;
