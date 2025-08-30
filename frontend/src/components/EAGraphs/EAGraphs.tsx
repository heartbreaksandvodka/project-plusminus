import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { AccountStatistics } from '../../services/api/statistics';
import { ManualStatistics } from '../../services/api/manualStatistics';
import './EAGraphs.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface EAGraphsProps {
  accountStats: AccountStatistics | null;
  manualStats: ManualStatistics | null;
}

const EAGraphs: React.FC<EAGraphsProps> = ({ accountStats, manualStats }) => {
  // EA vs Manual Performance Comparison Chart
  const performanceComparisonData = {
    labels: ['Win Rate', 'Total Trades', 'Profitability'],
    datasets: [
      {
        label: 'EA Performance',
        data: [
          accountStats?.ea_win_rate ?? 0,
          accountStats?.ea_total_trades ?? 0,
          accountStats?.ea_profitability_percent ?? 0
        ],
        backgroundColor: 'rgba(102, 126, 234, 0.6)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 2,
      },
      {
        label: 'Manual Performance',
        data: [
          manualStats?.win_rate ?? 0,
          manualStats?.total_trades ?? 0,
          manualStats?.profitability_percent ?? 0
        ],
        backgroundColor: 'rgba(34, 197, 94, 0.6)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 2,
      },
    ],
  };

  // EA Activity Timeline (Active EAs over time simulation)
  const eaActivityData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Active EAs',
        data: [2, 3, 1, 4, 3, accountStats?.ea_activity.length ?? 0],
        fill: false,
        borderColor: 'rgba(102, 126, 234, 1)',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.1,
      },
      {
        label: 'Running EAs',
        data: [1, 2, 1, 3, 2, accountStats?.running_eas ?? 0],
        fill: false,
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.1,
      },
    ],
  };

  // Trading Distribution Pie Chart
  const tradingDistributionData = {
    labels: ['EA Trades', 'Manual Trades'],
    datasets: [
      {
        data: [
          accountStats?.ea_total_trades ?? 0,
          manualStats?.total_trades ?? 0
        ],
        backgroundColor: [
          'rgba(102, 126, 234, 0.8)',
          'rgba(34, 197, 94, 0.8)',
        ],
        borderColor: [
          'rgba(102, 126, 234, 1)',
          'rgba(34, 197, 94, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  // Manual Trading Sessions Timeline
  const manualSessionsData = {
    labels: manualStats?.sessions?.slice(0, 5).map((_, idx) => `Session ${idx + 1}`) ?? ['No Sessions'],
    datasets: [
      {
        label: 'Profit/Loss per Session',
        data: manualStats?.sessions?.slice(0, 5).map(session => 
          session.profit_loss ?? 0
        ) ?? [0],
        backgroundColor: manualStats?.sessions?.slice(0, 5).map(session => {
          const pl = session.profit_loss ?? 0;
          return pl >= 0 ? 'rgba(34, 197, 94, 0.6)' : 'rgba(239, 68, 68, 0.6)';
        }) ?? ['rgba(156, 163, 175, 0.6)'],
        borderColor: manualStats?.sessions?.slice(0, 5).map(session => {
          const pl = session.profit_loss ?? 0;
          return pl >= 0 ? 'rgba(34, 197, 94, 1)' : 'rgba(239, 68, 68, 1)';
        }) ?? ['rgba(156, 163, 175, 1)'],
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        font: {
          size: 16,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        font: {
          size: 16,
        },
      },
    },
  };

  return (
    <div className="ea-graphs-container">
      <div className="graphs-grid">
        {/* EA vs Manual Performance Comparison */}
        <div className="graph-card">
          <h3>📊 EA vs Manual Performance</h3>
          <div className="chart-wrapper">
            <Bar 
              data={performanceComparisonData} 
              options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  title: {
                    ...chartOptions.plugins.title,
                    text: 'Performance Metrics Comparison',
                  },
                },
              }} 
            />
          </div>
        </div>

        {/* EA Activity Timeline */}
        <div className="graph-card">
          <h3>⚡ EA Activity Timeline</h3>
          <div className="chart-wrapper">
            <Line 
              data={eaActivityData} 
              options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  title: {
                    ...chartOptions.plugins.title,
                    text: 'EA Activity Over Time',
                  },
                },
              }} 
            />
          </div>
        </div>

        {/* Trading Distribution */}
        <div className="graph-card">
          <h3>🥧 Trading Distribution</h3>
          <div className="chart-wrapper">
            <Doughnut 
              data={tradingDistributionData} 
              options={{
                ...pieOptions,
                plugins: {
                  ...pieOptions.plugins,
                  title: {
                    ...pieOptions.plugins.title,
                    text: 'EA vs Manual Trades Distribution',
                  },
                },
              }} 
            />
          </div>
        </div>

        {/* Manual Trading Sessions */}
        <div className="graph-card">
          <h3>📝 Manual Trading Sessions P/L</h3>
          <div className="chart-wrapper">
            <Bar 
              data={manualSessionsData} 
              options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  title: {
                    ...chartOptions.plugins.title,
                    text: 'Profit/Loss per Manual Session',
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: 'rgba(0, 0, 0, 0.1)',
                    },
                  },
                  x: {
                    grid: {
                      display: false,
                    },
                  },
                },
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to use backend-calculated profitability directly
function calculateManualProfitability(manualStats: ManualStatistics | null): number {
  return manualStats?.profitability_percent ?? 0;
}

export default EAGraphs;
