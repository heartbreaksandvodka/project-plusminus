import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LoadingSpinner, Button } from '../components/common';
import './Algorithms.css';

interface Algorithm {
  id: number;
  name: string;
  description: string;
  category: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';
  requiredTier: 'free' | 'bronze' | 'gold' | 'premium';
  timeComplexity: string;
  spaceComplexity: string;
  useCases: string[];
  isLocked: boolean;
}

interface UserSubscription {
  tier: 'free' | 'bronze' | 'gold' | 'premium';
  status: 'active' | 'trial' | 'expired';
  trialDaysLeft?: number;
}

const Algorithms: React.FC = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { user } = useAuth();
  const navigate = useNavigate();
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [userSubscription, setUserSubscription] = useState<UserSubscription>({ tier: 'free', status: 'active' });
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

  useEffect(() => {
    fetchAlgorithms();
    fetchUserSubscription();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchAlgorithms = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockAlgorithms: Algorithm[] = [
        // Free Tier Algorithms
        {
          id: 1,
          name: 'Linear Search',
          description: 'Basic search algorithm that checks each element sequentially',
          category: 'Search',
          difficulty: 'Beginner',
          requiredTier: 'free',
          timeComplexity: 'O(n)',
          spaceComplexity: 'O(1)',
          useCases: ['Small datasets', 'Unsorted arrays', 'Simple searches'],
          isLocked: false
        },
        {
          id: 2,
          name: 'Bubble Sort',
          description: 'Simple sorting algorithm that repeatedly steps through the list',
          category: 'Sorting',
          difficulty: 'Beginner',
          requiredTier: 'free',
          timeComplexity: 'O(n²)',
          spaceComplexity: 'O(1)',
          useCases: ['Educational purposes', 'Small datasets', 'Nearly sorted data'],
          isLocked: false
        },
        {
          id: 3,
          name: 'Binary Search',
          description: 'Efficient search algorithm for sorted arrays',
          category: 'Search',
          difficulty: 'Beginner',
          requiredTier: 'free',
          timeComplexity: 'O(log n)',
          spaceComplexity: 'O(1)',
          useCases: ['Sorted arrays', 'Database indexing', 'Game development'],
          isLocked: false
        },
        
        // Bronze Tier Algorithms
        {
          id: 4,
          name: 'Quick Sort',
          description: 'Efficient divide-and-conquer sorting algorithm',
          category: 'Sorting',
          difficulty: 'Intermediate',
          requiredTier: 'bronze',
          timeComplexity: 'O(n log n)',
          spaceComplexity: 'O(log n)',
          useCases: ['General purpose sorting', 'Large datasets', 'System libraries'],
          isLocked: true
        },
        {
          id: 5,
          name: 'Merge Sort',
          description: 'Stable divide-and-conquer sorting algorithm',
          category: 'Sorting',
          difficulty: 'Intermediate',
          requiredTier: 'bronze',
          timeComplexity: 'O(n log n)',
          spaceComplexity: 'O(n)',
          useCases: ['Stable sorting', 'External sorting', 'Linked lists'],
          isLocked: true
        },
        {
          id: 6,
          name: 'Breadth-First Search',
          description: 'Graph traversal algorithm exploring neighbors first',
          category: 'Graph',
          difficulty: 'Intermediate',
          requiredTier: 'bronze',
          timeComplexity: 'O(V + E)',
          spaceComplexity: 'O(V)',
          useCases: ['Shortest path', 'Level order traversal', 'Social networks'],
          isLocked: true
        },

        // Gold Tier Algorithms
        {
          id: 7,
          name: 'Dijkstra\'s Algorithm',
          description: 'Shortest path algorithm for weighted graphs',
          category: 'Graph',
          difficulty: 'Advanced',
          requiredTier: 'gold',
          timeComplexity: 'O(V²)',
          spaceComplexity: 'O(V)',
          useCases: ['GPS navigation', 'Network routing', 'Game pathfinding'],
          isLocked: true
        },
        {
          id: 8,
          name: 'Dynamic Programming - LCS',
          description: 'Longest Common Subsequence using dynamic programming',
          category: 'Dynamic Programming',
          difficulty: 'Advanced',
          requiredTier: 'gold',
          timeComplexity: 'O(mn)',
          spaceComplexity: 'O(mn)',
          useCases: ['DNA sequencing', 'Version control', 'Plagiarism detection'],
          isLocked: true
        },
        {
          id: 9,
          name: 'A* Search Algorithm',
          description: 'Heuristic search algorithm for pathfinding',
          category: 'Graph',
          difficulty: 'Advanced',
          requiredTier: 'gold',
          timeComplexity: 'O(b^d)',
          spaceComplexity: 'O(b^d)',
          useCases: ['Game AI', 'Robotics', 'Route planning'],
          isLocked: true
        },

        // Premium Tier Algorithms
        {
          id: 10,
          name: 'Machine Learning - K-Means',
          description: 'Unsupervised clustering algorithm',
          category: 'Machine Learning',
          difficulty: 'Expert',
          requiredTier: 'premium',
          timeComplexity: 'O(nki)',
          spaceComplexity: 'O(n + k)',
          useCases: ['Customer segmentation', 'Image processing', 'Data mining'],
          isLocked: true
        },
        {
          id: 11,
          name: 'Neural Network - Backpropagation',
          description: 'Learning algorithm for artificial neural networks',
          category: 'Machine Learning',
          difficulty: 'Expert',
          requiredTier: 'premium',
          timeComplexity: 'O(n * h * o * i)',
          spaceComplexity: 'O(h + o)',
          useCases: ['Deep learning', 'Pattern recognition', 'AI systems'],
          isLocked: true
        },
        {
          id: 12,
          name: 'Advanced Cryptography - RSA',
          description: 'Public-key cryptosystem for secure communication',
          category: 'Cryptography',
          difficulty: 'Expert',
          requiredTier: 'premium',
          timeComplexity: 'O(log³ n)',
          spaceComplexity: 'O(1)',
          useCases: ['Secure communication', 'Digital signatures', 'Blockchain'],
          isLocked: true
        }
      ];

      setAlgorithms(mockAlgorithms);
    } catch (error) {
      console.error('Error fetching algorithms:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserSubscription = async () => {
    try {
      // Mock user subscription - replace with actual API call
      setUserSubscription({
        tier: 'free', // This would come from API based on user's actual subscription
        status: 'trial',
        trialDaysLeft: 7
      });
    } catch (error) {
      console.error('Error fetching user subscription:', error);
    }
  };

  const getTierAccess = (requiredTier: string): boolean => {
    const tierHierarchy = { free: 0, bronze: 1, gold: 2, premium: 3 };
    const userTierLevel = tierHierarchy[userSubscription.tier as keyof typeof tierHierarchy];
    const requiredTierLevel = tierHierarchy[requiredTier as keyof typeof tierHierarchy];
    
    return userTierLevel >= requiredTierLevel && userSubscription.status === 'active';
  };

  const updateAlgorithmAccess = (algorithms: Algorithm[]): Algorithm[] => {
    return algorithms.map(algorithm => ({
      ...algorithm,
      isLocked: !getTierAccess(algorithm.requiredTier)
    }));
  };

  const getFilteredAlgorithms = (): Algorithm[] => {
    let filtered = updateAlgorithmAccess(algorithms);

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(alg => alg.category === selectedCategory);
    }

    if (selectedDifficulty !== 'all') {
      filtered = filtered.filter(alg => alg.difficulty === selectedDifficulty);
    }

    return filtered;
  };

  const getUniqueCategories = (): string[] => {
    return Array.from(new Set(algorithms.map(alg => alg.category)));
  };

  const getTierColor = (tier: string): string => {
    switch (tier) {
      case 'free': return '#4CAF50';
      case 'bronze': return '#CD7F32';
      case 'gold': return '#FFD700';
      case 'premium': return '#9C27B0';
      default: return '#666';
    }
  };

  const getDifficultyColor = (difficulty: string): string => {
    switch (difficulty) {
      case 'Beginner': return '#4CAF50';
      case 'Intermediate': return '#FF9800';
      case 'Advanced': return '#F44336';
      case 'Expert': return '#9C27B0';
      default: return '#666';
    }
  };

  const handleAlgorithmAccess = (algorithm: Algorithm) => {
    if (algorithm.isLocked) {
      navigate('/subscriptions');
    } else {
      // Navigate to algorithm detail page or open algorithm
      console.log(`Opening algorithm: ${algorithm.name}`);
    }
  };

  if (loading) {
    return (
      <div className="algorithms-container">
        <div className="loading-container">
          <LoadingSpinner />
          <p>Loading algorithms...</p>
        </div>
      </div>
    );
  }

  const filteredAlgorithms = getFilteredAlgorithms();
  const categories = getUniqueCategories();

  return (
    <div className="algorithms-container">
      <div className="algorithms-content">
        <div className="algorithms-header">
          <div className="header-content">
            <h2>🧮 Algorithm Library</h2>
            <p>Master algorithms based on your subscription tier</p>
            {userSubscription.status === 'trial' && (
              <div className="trial-banner">
                🚀 Free Trial: {userSubscription.trialDaysLeft} days remaining
              </div>
            )}
          </div>
          <Button 
            onClick={() => navigate('/dashboard')} 
            variant="secondary"
          >
            ← Back to Dashboard
          </Button>
        </div>

        {/* Subscription Status */}
        <div className="subscription-status">
          <div className="current-tier">
            <span className="tier-label">Current Tier:</span>
            <span 
              className="tier-badge"
              style={{ backgroundColor: getTierColor(userSubscription.tier) }}
            >
              {userSubscription.tier.toUpperCase()}
            </span>
          </div>
          <Button 
            onClick={() => navigate('/subscriptions')}
            variant="primary"
            size="small"
          >
            Upgrade Plan
          </Button>
        </div>

        {/* Filters */}
        <div className="filters-section">
          <div className="filter-group">
            <label>Category:</label>
            <select 
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Difficulty:</label>
            <select 
              value={selectedDifficulty} 
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Levels</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
              <option value="Expert">Expert</option>
            </select>
          </div>
        </div>

        {/* Algorithms Grid */}
        <div className="algorithms-grid">
          {filteredAlgorithms.map((algorithm) => (
            <div 
              key={algorithm.id} 
              className={`algorithm-card ${algorithm.isLocked ? 'locked' : ''}`}
              onClick={() => handleAlgorithmAccess(algorithm)}
            >
              {algorithm.isLocked && (
                <div className="lock-overlay">
                  <div className="lock-icon">🔒</div>
                  <p>Upgrade to {algorithm.requiredTier.toUpperCase()} to unlock</p>
                </div>
              )}

              <div className="algorithm-header">
                <h3>{algorithm.name}</h3>
                <div className="algorithm-badges">
                  <span 
                    className="tier-badge"
                    style={{ backgroundColor: getTierColor(algorithm.requiredTier) }}
                  >
                    {algorithm.requiredTier.toUpperCase()}
                  </span>
                  <span 
                    className="difficulty-badge"
                    style={{ backgroundColor: getDifficultyColor(algorithm.difficulty) }}
                  >
                    {algorithm.difficulty}
                  </span>
                </div>
              </div>

              <p className="algorithm-description">{algorithm.description}</p>

              <div className="algorithm-complexity">
                <div className="complexity-item">
                  <span className="complexity-label">Time:</span>
                  <span className="complexity-value">{algorithm.timeComplexity}</span>
                </div>
                <div className="complexity-item">
                  <span className="complexity-label">Space:</span>
                  <span className="complexity-value">{algorithm.spaceComplexity}</span>
                </div>
              </div>

              <div className="algorithm-category">
                <span className="category-tag">{algorithm.category}</span>
              </div>

              <div className="use-cases">
                <h4>Use Cases:</h4>
                <ul>
                  {algorithm.useCases.slice(0, 2).map((useCase, index) => (
                    <li key={index}>{useCase}</li>
                  ))}
                  {algorithm.useCases.length > 2 && (
                    <li className="more-cases">+{algorithm.useCases.length - 2} more</li>
                  )}
                </ul>
              </div>

              <div className="algorithm-action">
                {algorithm.isLocked ? (
                  <Button variant="secondary" size="small">
                    🔓 Unlock with {algorithm.requiredTier.toUpperCase()}
                  </Button>
                ) : (
                  <Button variant="primary" size="small">
                    📖 Study Algorithm
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredAlgorithms.length === 0 && (
          <div className="no-algorithms">
            <div className="no-algorithms-icon">🔍</div>
            <h3>No Algorithms Found</h3>
            <p>Try adjusting your filters to see more algorithms.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Algorithms;
