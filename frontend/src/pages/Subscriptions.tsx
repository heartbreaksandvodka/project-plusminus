import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Subscriptions.css';

interface Subscription {
  id: number;
  name: string;
  description: string;
  price: string;
  status: 'active' | 'inactive' | 'cancelled';
  next_billing: string;
}

const Subscriptions: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/subscriptions/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        // For demo purposes, we'll show some mock data
        setSubscriptions([
          {
            id: 1,
            name: 'Premium Plan',
            description: 'Access to all premium features',
            price: '$19.99/month',
            status: 'active',
            next_billing: '2024-02-15'
          },
          {
            id: 2,
            name: 'Basic Plan',
            description: 'Essential features for getting started',
            price: '$9.99/month',
            status: 'inactive',
            next_billing: '2024-02-01'
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
      case 'inactive':
        return '#FFC107';
      case 'cancelled':
        return '#F44336';
      default:
        return '#9E9E9E';
    }
  };

  const handleManageSubscription = (subscriptionId: number) => {
    // This would typically handle subscription management
    console.log('Managing subscription:', subscriptionId);
  };

  if (loading) {
    return (
      <div className="subscriptions-container">
        <div className="loading">Loading subscriptions...</div>
      </div>
    );
  }

  return (
    <div className="subscriptions-container">
      <div className="subscriptions-content">
        <div className="subscriptions-header">
          <h2>Your Subscriptions</h2>
          <button 
            onClick={() => navigate('/dashboard')} 
            className="back-button"
          >
            Back to Dashboard
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {subscriptions.length === 0 ? (
          <div className="no-subscriptions">
            <div className="no-subscriptions-icon">📋</div>
            <h3>No Subscriptions Found</h3>
            <p>You don't have any active subscriptions yet.</p>
            <button className="explore-button">Explore Plans</button>
          </div>
        ) : (
          <div className="subscriptions-grid">
            {subscriptions.map((subscription) => (
              <div key={subscription.id} className="subscription-card">
                <div className="subscription-header">
                  <h3>{subscription.name}</h3>
                  <span 
                    className="subscription-status"
                    style={{ backgroundColor: getStatusColor(subscription.status) }}
                  >
                    {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
                  </span>
                </div>
                
                <p className="subscription-description">{subscription.description}</p>
                
                <div className="subscription-details">
                  <div className="subscription-price">{subscription.price}</div>
                  <div className="subscription-billing">
                    Next billing: {new Date(subscription.next_billing).toLocaleDateString()}
                  </div>
                </div>
                
                <div className="subscription-actions">
                  <button 
                    onClick={() => handleManageSubscription(subscription.id)}
                    className="manage-button"
                  >
                    Manage
                  </button>
                  {subscription.status === 'active' && (
                    <button className="cancel-subscription-button">
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="subscriptions-footer">
          <div className="billing-info">
            <h3>Billing Information</h3>
            <p>All subscriptions are billed automatically to your default payment method.</p>
            <button className="payment-method-button">
              Update Payment Method
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Subscriptions;
