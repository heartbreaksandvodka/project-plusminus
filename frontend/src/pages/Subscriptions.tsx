import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LoadingSpinner, Button } from '../components/common';
import './Subscriptions.css';

interface Subscription {
  id: number;
  name: string;
  description: string;
  price: string;
  originalPrice?: string;
  status: 'active' | 'inactive' | 'cancelled' | 'trial';
  next_billing: string;
  features: string[];
  discount?: number;
  trial_days?: number;
}

interface Plan {
  id: number;
  name: string;
  description: string;
  price: string;
  originalPrice?: string;
  features: string[];
  recommended?: boolean;
  discount?: number;
  trial_days?: number;
}

const Subscriptions: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [availablePlans, setAvailablePlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'subscriptions' | 'plans'>('subscriptions');
  const [showCancelModal, setShowCancelModal] = useState<number | null>(null);

  useEffect(() => {
    fetchSubscriptions();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/subscriptions/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        // For demo purposes, we'll show some mock data instead of using the API response
        setSubscriptions([
          {
            id: 1,
            name: 'Gold Plan',
            description: 'Advanced algorithms for professional developers',
            price: 'R899/month',
            originalPrice: 'R1299/month',
            status: 'active',
            next_billing: '2024-02-15',
            features: [
              'Advanced graph algorithms',
              'Dynamic programming solutions',
              'Priority customer support',
              'Interactive visualizations',
              'Algorithm optimization tips'
            ],
            discount: 31
          },
          {
            id: 2,
            name: 'Bronze Plan',
            description: 'Enhanced algorithms for growing developers',
            price: 'R249/month',
            status: 'trial',
            next_billing: '2024-02-01',
            features: [
              'Advanced sorting algorithms',
              'Graph traversal algorithms',
              'Email support',
              'Basic complexity analysis'
            ],
            trial_days: 7
          }
        ]);

        // Mock available plans
        setAvailablePlans([
          {
            id: 1,
            name: 'Bronze',
            description: 'Enhanced algorithms for growing developers',
            price: 'R249/month',
            features: [
              'All Free algorithms',
              'Advanced sorting algorithms',
              'Graph traversal algorithms',
              'Email support',
              'Basic complexity analysis',
              'Code examples'
            ]
          },
          {
            id: 2,
            name: 'Gold',
            description: 'Advanced algorithms for professional developers',
            price: 'R899/month',
            originalPrice: 'R1299/month',
            features: [
              'All Bronze features',
              'Advanced graph algorithms',
              'Dynamic programming',
              'Priority support',
              'Detailed complexity analysis',
              'Interactive visualizations',
              'Algorithm optimization tips'
            ],
            recommended: true,
            discount: 31
          },
          {
            id: 3,
            name: 'Premium',
            description: 'Complete algorithm mastery for experts',
            price: 'R1299/month',
            features: [
              'All Gold features',
              'Machine Learning algorithms',
              'Advanced cryptography',
              'Dedicated support',
              'Custom algorithm requests',
              'White-label solutions',
              'Algorithm performance benchmarking',
              'Access to cutting-edge research'
            ]
          }
        ]);
      } else {
        setError('Failed to fetch subscriptions');
      }
    } catch (err) {
      setError('An error occurred while fetching subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#4CAF50';
      case 'trial':
        return '#2196F3';
      case 'inactive':
        return '#FFC107';
      case 'cancelled':
        return '#F44336';
      default:
        return '#9E9E9E';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return '✓';
      case 'trial':
        return '🚀';
      case 'inactive':
        return '⏸️';
      case 'cancelled':
        return '❌';
      default:
        return '?';
    }
  };

  const handleManageSubscription = (subscriptionId: number) => {
    console.log('Managing subscription:', subscriptionId);
    // This would typically open a subscription management modal
  };

  const handleCancelSubscription = (subscriptionId: number) => {
    setShowCancelModal(subscriptionId);
  };

  const confirmCancelSubscription = () => {
    if (showCancelModal) {
      setSubscriptions(prev => 
        prev.map(sub => 
          sub.id === showCancelModal 
            ? { ...sub, status: 'cancelled' }
            : sub
        )
      );
      setShowCancelModal(null);
    }
  };

  const handleSubscribeToPlan = (planId: number) => {
    console.log('Subscribing to plan:', planId);
    // This would typically handle the subscription process
  };

  if (loading) {
    return (
      <div className="subscriptions-container">
        <div className="loading-container">
          <LoadingSpinner />
          <p>Loading subscriptions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="subscriptions-container">
      <div className="subscriptions-content">
        <div className="subscriptions-header">
          <div className="header-content">
            <h2>💳 Subscription Management</h2>
            <p>Manage your subscriptions and explore new plans</p>
          </div>
          <Button 
            onClick={() => navigate('/dashboard')} 
            variant="secondary"
          >
            ← Back to Dashboard
          </Button>
        </div>

        {error && (
          <div className="error-message">
            <span>⚠️</span>
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'subscriptions' ? 'active' : ''}`}
            onClick={() => setActiveTab('subscriptions')}
          >
            Your Subscriptions ({subscriptions.length})
          </button>
          <button 
            className={`tab-button ${activeTab === 'plans' ? 'active' : ''}`}
            onClick={() => setActiveTab('plans')}
          >
            Available Plans ({availablePlans.length})
          </button>
        </div>

        {/* Your Subscriptions Tab */}
        {activeTab === 'subscriptions' && (
          <div className="tab-content">
            {subscriptions.length === 0 ? (
              <div className="no-subscriptions">
                <div className="no-subscriptions-icon">📋</div>
                <h3>No Active Subscriptions</h3>
                <p>You don't have any subscriptions yet. Explore our plans to get started!</p>
                <Button 
                  onClick={() => setActiveTab('plans')}
                  variant="primary"
                  size="large"
                >
                  Explore Plans
                </Button>
              </div>
            ) : (
              <div className="subscriptions-grid">
                {subscriptions.map((subscription) => (
                  <div key={subscription.id} className="subscription-card">
                    <div className="subscription-header">
                      <div className="subscription-title">
                        <h3>{subscription.name}</h3>
                        {subscription.discount && (
                          <span className="discount-badge">
                            {subscription.discount}% OFF
                          </span>
                        )}
                      </div>
                      <span 
                        className="subscription-status"
                        style={{ backgroundColor: getStatusColor(subscription.status) }}
                      >
                        {getStatusIcon(subscription.status)} {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
                      </span>
                    </div>
                    
                    <p className="subscription-description">{subscription.description}</p>
                    
                    <div className="subscription-pricing">
                      {subscription.originalPrice && (
                        <span className="original-price">{subscription.originalPrice}</span>
                      )}
                      <div className="subscription-price">{subscription.price}</div>
                      {subscription.trial_days && (
                        <div className="trial-info">
                          🎯 {subscription.trial_days} days trial remaining
                        </div>
                      )}
                    </div>

                    <div className="features-list">
                      <h4>Features:</h4>
                      <ul>
                        {subscription.features.slice(0, 3).map((feature, index) => (
                          <li key={index}>✓ {feature}</li>
                        ))}
                        {subscription.features.length > 3 && (
                          <li className="more-features">
                            +{subscription.features.length - 3} more features
                          </li>
                        )}
                      </ul>
                    </div>
                    
                    <div className="subscription-details">
                      <div className="subscription-billing">
                        📅 Next billing: {new Date(subscription.next_billing).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div className="subscription-actions">
                      <Button 
                        onClick={() => handleManageSubscription(subscription.id)}
                        variant="primary"
                        size="small"
                      >
                        Manage
                      </Button>
                      {subscription.status === 'active' && (
                        <Button
                          onClick={() => handleCancelSubscription(subscription.id)}
                          variant="danger"
                          size="small"
                        >
                          Cancel
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Available Plans Tab */}
        {activeTab === 'plans' && (
          <div className="tab-content">
            <div className="plans-header">
              <h3>Choose Your Perfect Plan</h3>
              <p>Upgrade or downgrade anytime. All plans include a 30-day money-back guarantee.</p>
            </div>
            
            <div className="plans-grid">
              {availablePlans.map((plan) => (
                <div 
                  key={plan.id} 
                  className={`plan-card ${plan.recommended ? 'recommended' : ''}`}
                >
                  {plan.recommended && (
                    <div className="recommended-badge">🌟 Most Popular</div>
                  )}
                  
                  <div className="plan-header">
                    <h3>{plan.name}</h3>
                    <p className="plan-description">{plan.description}</p>
                  </div>
                  
                  <div className="plan-pricing">
                    {plan.originalPrice && (
                      <span className="original-price">{plan.originalPrice}</span>
                    )}
                    <div className="plan-price">{plan.price}</div>
                    {plan.discount && (
                      <div className="savings">Save {plan.discount}%</div>
                    )}
                  </div>
                  
                  <div className="plan-features">
                    <ul>
                      {plan.features.map((feature, index) => (
                        <li key={index}>✓ {feature}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <Button 
                    onClick={() => handleSubscribeToPlan(plan.id)}
                    variant={plan.recommended ? "primary" : "secondary"}
                    size="large"
                  >
                    {plan.trial_days ? `Start ${plan.trial_days}-Day Free Trial` : 'Subscribe Now'}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Cancel Subscription Modal */}
        {showCancelModal && (
          <div className="modal-overlay">
            <div className="cancel-modal">
              <h3>⚠️ Cancel Subscription</h3>
              <p>Are you sure you want to cancel this subscription? You'll lose access to all premium features at the end of your current billing period.</p>
              <div className="modal-actions">
                <Button 
                  onClick={() => setShowCancelModal(null)}
                  variant="secondary"
                >
                  Keep Subscription
                </Button>
                <Button 
                  onClick={confirmCancelSubscription}
                  variant="danger"
                >
                  Yes, Cancel
                </Button>
              </div>
            </div>
          </div>
        )}

        <div className="subscriptions-footer">
          <div className="billing-info">
            <h3>💳 Billing Information</h3>
            <p>All subscriptions are billed automatically to your default payment method. You can change or update your payment method at any time.</p>
            <Button 
              variant="secondary"
              onClick={() => console.log('Update payment method')}
            >
              Update Payment Method
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Subscriptions;
