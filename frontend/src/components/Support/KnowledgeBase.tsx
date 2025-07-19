import React, { useState } from 'react';

interface KnowledgeBaseItem {
  id: string;
  title: string;
  category: string;
  content: string;
  tags: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

interface KnowledgeBaseProps {
  isOpen: boolean;
  onClose: () => void;
}

const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({ isOpen, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedArticle, setSelectedArticle] = useState<KnowledgeBaseItem | null>(null);

  const knowledgeBaseItems: KnowledgeBaseItem[] = [
    {
      id: '1',
      title: 'How to Connect Your MT5 Account',
      category: 'getting-started',
      content: `
        <h3>Connecting Your MT5 Account</h3>
        <p>Follow these steps to connect your MetaTrader 5 account:</p>
        <ol>
          <li>Navigate to the Algorithm page</li>
          <li>Click on the MT5 Account dropdown</li>
          <li>Select "Add New Account"</li>
          <li>Enter your broker details and account credentials</li>
          <li>Click "Connect" and wait for verification</li>
        </ol>
        <p><strong>Important:</strong> Ensure your broker supports algorithmic trading and API access.</p>
      `,
      tags: ['mt5', 'connection', 'setup'],
      difficulty: 'beginner'
    },
    {
      id: '2',
      title: 'Understanding Risk Management Settings',
      category: 'risk-management',
      content: `
        <h3>Risk Management Parameters</h3>
        <ul>
          <li><strong>Max Loss Per Trade:</strong> Maximum percentage of account balance that can be lost on a single trade</li>
          <li><strong>Max Daily Loss:</strong> Maximum percentage loss allowed per trading day</li>
          <li><strong>Position Size:</strong> Percentage of account balance to risk per position</li>
          <li><strong>Stop Loss:</strong> Automatic exit point to limit losses</li>
          <li><strong>Take Profit:</strong> Automatic exit point to secure profits</li>
          <li><strong>Max Consecutive Losses:</strong> Number of consecutive losing trades before algorithm pauses</li>
        </ul>
        <p>Recommended settings for beginners: Max Loss Per Trade: 1-2%, Daily Loss: 3-5%, Position Size: 1-2%</p>
      `,
      tags: ['risk', 'management', 'settings', 'safety'],
      difficulty: 'intermediate'
    },
    {
      id: '3',
      title: 'Algorithm Performance Metrics Explained',
      category: 'performance',
      content: `
        <h3>Key Performance Indicators</h3>
        <ul>
          <li><strong>ROI (Return on Investment):</strong> Percentage gain/loss over time periods</li>
          <li><strong>Win Rate:</strong> Percentage of profitable trades vs total trades</li>
          <li><strong>Profit Factor:</strong> Ratio of gross profit to gross loss (>1.0 is profitable)</li>
          <li><strong>Total Trades:</strong> Number of trades executed by the algorithm</li>
          <li><strong>Drawdown:</strong> Peak-to-trough decline in account value</li>
        </ul>
        <p>A good algorithm typically has: Win Rate >60%, Profit Factor >1.5, Max Drawdown <20%</p>
      `,
      tags: ['performance', 'metrics', 'roi', 'analysis'],
      difficulty: 'intermediate'
    },
    {
      id: '4',
      title: 'Troubleshooting Common Issues',
      category: 'troubleshooting',
      content: `
        <h3>Common Problems and Solutions</h3>
        <h4>Algorithm Won't Deploy</h4>
        <ul>
          <li>Check MT5 account connection status</li>
          <li>Verify sufficient account balance</li>
          <li>Ensure risk management settings are valid</li>
          <li>Check if markets are open for selected symbol</li>
        </ul>
        
        <h4>Poor Performance</h4>
        <ul>
          <li>Review and adjust risk management settings</li>
          <li>Check market conditions and volatility</li>
          <li>Consider switching to different symbols</li>
          <li>Monitor news events affecting your trading instruments</li>
        </ul>
        
        <h4>Connection Problems</h4>
        <ul>
          <li>Restart MT5 platform</li>
          <li>Check internet connection</li>
          <li>Verify broker server status</li>
          <li>Update MT5 to latest version</li>
        </ul>
      `,
      tags: ['troubleshooting', 'problems', 'solutions', 'debugging'],
      difficulty: 'beginner'
    },
    {
      id: '5',
      title: 'Advanced Algorithm Optimization',
      category: 'advanced',
      content: `
        <h3>Optimizing Algorithm Performance</h3>
        <h4>Parameter Tuning</h4>
        <ul>
          <li>Backtest different risk management settings</li>
          <li>Adjust position sizing based on volatility</li>
          <li>Optimize take profit and stop loss ratios</li>
          <li>Fine-tune consecutive loss limits</li>
        </ul>
        
        <h4>Market Condition Adaptation</h4>
        <ul>
          <li>Monitor correlation between algorithms</li>
          <li>Adjust exposure during high volatility</li>
          <li>Use multiple timeframes for confirmation</li>
          <li>Implement dynamic position sizing</li>
        </ul>
        
        <h4>Portfolio Management</h4>
        <ul>
          <li>Diversify across different asset classes</li>
          <li>Balance high and low risk algorithms</li>
          <li>Monitor overall portfolio drawdown</li>
          <li>Rebalance based on performance</li>
        </ul>
      `,
      tags: ['optimization', 'advanced', 'tuning', 'portfolio'],
      difficulty: 'advanced'
    }
  ];

  const categories = [
    { id: 'all', name: 'All Categories', icon: '📚' },
    { id: 'getting-started', name: 'Getting Started', icon: '🚀' },
    { id: 'risk-management', name: 'Risk Management', icon: '🛡️' },
    { id: 'performance', name: 'Performance', icon: '📊' },
    { id: 'troubleshooting', name: 'Troubleshooting', icon: '🔧' },
    { id: 'advanced', name: 'Advanced', icon: '⚡' }
  ];

  const filteredItems = knowledgeBaseItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '#10b981';
      case 'intermediate': return '#f59e0b';
      case 'advanced': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="kb-modal-enhanced" onClick={(e) => e.stopPropagation()}>
        <div className="kb-header">
          <h3>📚 Knowledge Base</h3>
          <button onClick={onClose}>✕</button>
        </div>
        
        <div className="kb-content-wrapper">
          <div className="kb-sidebar">
            <div className="kb-search">
              <input
                type="text"
                placeholder="Search articles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="kb-search-input"
              />
            </div>
            
            <div className="kb-categories">
              {categories.map(category => (
                <button
                  key={category.id}
                  className={`kb-category-btn ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category.id)}
                >
                  <span className="category-icon">{category.icon}</span>
                  <span className="category-name">{category.name}</span>
                </button>
              ))}
            </div>
          </div>
          
          <div className="kb-main">
            {selectedArticle ? (
              <div className="kb-article">
                <button 
                  className="kb-back-btn"
                  onClick={() => setSelectedArticle(null)}
                >
                  ← Back to Articles
                </button>
                <div className="kb-article-header">
                  <h2>{selectedArticle.title}</h2>
                  <span 
                    className="difficulty-badge"
                    style={{ backgroundColor: getDifficultyColor(selectedArticle.difficulty) }}
                  >
                    {selectedArticle.difficulty}
                  </span>
                </div>
                <div 
                  className="kb-article-content"
                  dangerouslySetInnerHTML={{ __html: selectedArticle.content }}
                />
                <div className="kb-article-tags">
                  {selectedArticle.tags.map(tag => (
                    <span key={tag} className="kb-tag">#{tag}</span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="kb-article-list">
                <h3>
                  {selectedCategory === 'all' ? 'All Articles' : 
                   categories.find(c => c.id === selectedCategory)?.name} 
                  ({filteredItems.length})
                </h3>
                <div className="kb-articles">
                  {filteredItems.map(item => (
                    <div 
                      key={item.id} 
                      className="kb-article-card"
                      onClick={() => setSelectedArticle(item)}
                    >
                      <div className="kb-article-card-header">
                        <h4>{item.title}</h4>
                        <span 
                          className="difficulty-badge small"
                          style={{ backgroundColor: getDifficultyColor(item.difficulty) }}
                        >
                          {item.difficulty}
                        </span>
                      </div>
                      <p className="kb-article-preview">
                        {item.content.replace(/<[^>]*>/g, '').substring(0, 120)}...
                      </p>
                      <div className="kb-article-meta">
                        <div className="kb-tags-preview">
                          {item.tags.slice(0, 3).map(tag => (
                            <span key={tag} className="kb-tag small">#{tag}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {filteredItems.length === 0 && (
                  <div className="kb-no-results">
                    <p>No articles found matching your search criteria.</p>
                    <button onClick={() => { setSearchTerm(''); setSelectedCategory('all'); }}>
                      Clear Filters
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase;
