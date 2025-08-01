"""
Test suite for High-Frequency Scalping EA
Tests basic functionality and MT5 connectivity
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestHFScalpingEA(unittest.TestCase):
    """Test cases for High-Frequency Scalping EA"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock MT5 to avoid requiring actual connection
        self.mt5_mock = Mock()
        
        with patch('mt5_hf_scalping_ea.mt5', self.mt5_mock):
            from mt5_hf_scalping_ea import HighFrequencyScalpingEA
            self.ea = HighFrequencyScalpingEA()
            
            # Add missing attributes for testing
            self.ea.point = 0.00001  # For 5-digit broker
            self.ea.digits = 5
            
            # Mock symbol info
            mock_symbol_info = Mock()
            mock_symbol_info.point = 0.00001
            mock_symbol_info.digits = 5
            mock_symbol_info.trade_tick_value = 1.0
            mock_symbol_info.volume_min = 0.01
            mock_symbol_info.volume_max = 100.0
            mock_symbol_info.volume_step = 0.01
            self.ea.symbol_info = mock_symbol_info
    
    def test_ea_initialization(self):
        """Test EA initialization"""
        self.assertIsNotNone(self.ea)
        self.assertEqual(self.ea.symbol, "BTCUSD")  # Updated to BTCUSD
        self.assertEqual(self.ea.magic_number, 54321)
        self.assertEqual(self.ea.scalp_target_percent, 3.0)  # Updated to 3% percentage-based
        self.assertEqual(self.ea.stop_loss_percent, 3.0)  # Updated to 3% percentage-based
        
    def test_configuration_import(self):
        """Test configuration file import"""
        try:
            import config
            self.assertTrue(hasattr(config, 'SYMBOL'))
            self.assertTrue(hasattr(config, 'MAGIC_NUMBER'))
            self.assertTrue(hasattr(config, 'SCALP_TARGET_PERCENT'))  # Updated to percentage-based
            self.assertTrue(hasattr(config, 'STOP_LOSS_PERCENT'))     # Updated to percentage-based
        except ImportError:
            self.fail("Configuration file not found")
    
    def test_price_data_structure(self):
        """Test price data structure"""
        mock_prices = {
            'time': 1627383600,
            'bid': 1.18450,
            'ask': 1.18453,
            'spread': 0.3,
            'volume': 100
        }
        
        # Test that price data has required fields
        required_fields = ['time', 'bid', 'ask', 'spread']
        for field in required_fields:
            self.assertIn(field, mock_prices)
    
    def test_signal_generation_logic(self):
        """Test signal generation logic"""
        # Mock metrics for testing
        test_metrics = {
            'price_momentum': 3.0,  # Strong upward momentum
            'pressure_ratio': 1.3,  # Ask pressure dominant
            'volume_bias': 1.5,     # Volume bias upward
            'spread_pressure': -0.2, # Spread tightening
            'current_spread': 3.0    # Good spread
        }
        
        with patch.object(self.ea, 'get_current_prices') as mock_prices:
            mock_prices.return_value = {'spread': 3.0}
            
            signal = self.ea.generate_scalping_signal(test_metrics)
            
            self.assertIn(signal['signal'], ['BUY', 'SELL', 'NONE'])
            self.assertIsInstance(signal['strength'], float)
            self.assertGreaterEqual(signal['strength'], 0.0)
            self.assertLessEqual(signal['strength'], 1.0)
    
    def test_position_size_calculation(self):
        """Test position size calculation"""
        # Mock account info
        mock_account = Mock()
        mock_account.balance = 10000.0
        mock_account.equity = 10000.0
        
        # Mock symbol info
        mock_symbol = Mock()
        mock_symbol.trade_tick_value = 1.0
        mock_symbol.volume_min = 0.01
        mock_symbol.volume_max = 100.0
        mock_symbol.volume_step = 0.01
        
        self.ea.symbol_info = mock_symbol
        
        with patch('mt5_hf_scalping_ea.mt5.account_info', return_value=mock_account):
            position_size = self.ea.calculate_position_size()
            
            self.assertIsInstance(position_size, float)
            self.assertGreater(position_size, 0)
            self.assertGreaterEqual(position_size, mock_symbol.volume_min)
            self.assertLessEqual(position_size, mock_symbol.volume_max)
    
    def test_order_flow_metrics(self):
        """Test order flow metrics calculation"""
        import pandas as pd
        
        # Create mock tick data
        mock_data = {
            'time': [1627383600, 1627383601, 1627383602, 1627383603, 1627383604],
            'bid': [1.18450, 1.18452, 1.18455, 1.18453, 1.18456],
            'ask': [1.18453, 1.18455, 1.18458, 1.18456, 1.18459],
            'spread': [0.3, 0.3, 0.3, 0.3, 0.3],
            'volume': [100, 150, 120, 180, 110]
        }
        
        df = pd.DataFrame(mock_data)
        metrics = self.ea.calculate_flow_metrics(df)
        
        # Verify metrics are calculated
        expected_metrics = ['price_momentum', 'pressure_ratio', 'volume_bias', 
                          'spread_pressure', 'tick_frequency', 'current_spread']
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], (int, float))
    
    def test_trading_time_logic(self):
        """Test trading time logic"""
        with patch('mt5_hf_scalping_ea.datetime') as mock_datetime:
            # Test trading hours (10 AM GMT, Wednesday)
            mock_datetime.now.return_value = Mock()
            mock_datetime.now.return_value.hour = 10
            mock_datetime.now.return_value.weekday.return_value = 2  # Wednesday
            
            is_trading_time = self.ea.is_trading_time()
            self.assertTrue(is_trading_time)
            
            # Test non-trading hours (6 AM GMT)
            mock_datetime.now.return_value.hour = 6
            is_trading_time = self.ea.is_trading_time()
            self.assertFalse(is_trading_time)
            
            # Test weekend (Saturday)
            mock_datetime.now.return_value.hour = 10
            mock_datetime.now.return_value.weekday.return_value = 5  # Saturday
            is_trading_time = self.ea.is_trading_time()
            self.assertFalse(is_trading_time)
    
    def test_daily_limits(self):
        """Test daily trading limits"""
        # Test daily trade limit
        self.ea.daily_trades = 100  # MAX_DAILY_TRADES
        
        mock_prices = {
            'time': 1627383600,
            'bid': 1.18450,
            'ask': 1.18453,
            'spread': 3.0
        }
        
        # Should not place order when limit reached
        with patch.object(self.ea, 'get_current_prices', return_value=mock_prices):
            result = self.ea.place_scalping_order('BUY', mock_prices)
            self.assertFalse(result)
    
    def test_spread_filtering(self):
        """Test spread filtering logic"""
        # Test wide spread rejection
        wide_spread_metrics = {
            'price_momentum': 3.0,
            'pressure_ratio': 1.3,
            'volume_bias': 1.5,
            'spread_pressure': -0.2,
            'current_spread': 15.0  # Too wide
        }
        
        signal = self.ea.generate_scalping_signal(wide_spread_metrics)
        self.assertEqual(signal['signal'], 'NONE')
        self.assertEqual(signal['reason'], 'Spread too wide')
        
        # Test narrow spread rejection
        narrow_spread_metrics = {
            'price_momentum': 3.0,
            'pressure_ratio': 1.3,
            'volume_bias': 1.5,
            'spread_pressure': -0.2,
            'current_spread': 1.0  # Too narrow
        }
        
        signal = self.ea.generate_scalping_signal(narrow_spread_metrics)
        self.assertEqual(signal['signal'], 'NONE')
        self.assertEqual(signal['reason'], 'Spread too narrow')
    
    def test_risk_management(self):
        """Test risk management features"""
        # Test percentage-based risk calculation
        mock_prices = {'bid': 1.18450, 'ask': 1.18453}
        
        # Mock account balance
        with patch.object(self.ea, 'get_account_balance', return_value=10000.0):
            # Test percentage calculation
            risk_amount = self.ea.calculate_percentage_amount(3.0)  # 3% of 10000 = 300
            self.assertEqual(risk_amount, 300.0)
            
            # Test price calculation for percentage-based levels
            buy_tp = self.ea.calculate_price_from_percentage(3.0, mock_prices['ask'], 'BUY')
            sell_tp = self.ea.calculate_price_from_percentage(3.0, mock_prices['bid'], 'SELL')
            
            # Verify prices are calculated correctly
            self.assertGreater(buy_tp, mock_prices['ask'])  # TP should be above entry for BUY
            self.assertLess(sell_tp, mock_prices['bid'])    # TP should be below entry for SELL
    
    def test_performance_tracking(self):
        """Test performance tracking"""
        # Initialize performance counters
        self.ea.total_trades = 50
        self.ea.winning_trades = 32
        self.ea.daily_trades = 25
        self.ea.daily_profit_percent = 1.5  # 1.5% of account
        
        # Mock account info
        mock_account = Mock()
        mock_account.balance = 10000.0
        mock_account.equity = 10150.0
        
        with patch('mt5_hf_scalping_ea.mt5.account_info', return_value=mock_account):
            stats = self.ea.get_performance_stats()
            
            self.assertEqual(stats['total_trades'], 50)
            self.assertEqual(stats['daily_trades'], 25)
            self.assertEqual(stats['daily_profit_percent'], 1.5)  # Updated to percentage-based
            self.assertEqual(stats['win_rate'], 64.0)  # 32/50 * 100
            self.assertEqual(stats['account_balance'], 10000.0)
            self.assertEqual(stats['account_equity'], 10150.0)

class TestConfiguration(unittest.TestCase):
    """Test configuration parameters"""
    
    def test_config_values(self):
        """Test configuration values are reasonable"""
        import config
        
        # Test percentage-based scalping parameters are reasonable
        self.assertGreater(config.SCALP_TARGET_PERCENT, 0)
        self.assertLess(config.SCALP_TARGET_PERCENT, 10)  # Reasonable percentage target
        
        self.assertGreaterEqual(config.STOP_LOSS_PERCENT, config.SCALP_TARGET_PERCENT)  # SL should be >= target (1:1 ratio is acceptable)
        self.assertLess(config.STOP_LOSS_PERCENT, 20)  # Reasonable percentage stop loss
        
        self.assertGreater(config.MAX_SPREAD, config.MIN_SPREAD)
        self.assertLess(config.MAX_SPREAD, 20)  # Reasonable spread limit
        
        # Test daily limits
        self.assertGreater(config.MAX_DAILY_TRADES, 0)
        self.assertLess(config.MAX_DAILY_TRADES, 500)  # Reasonable daily limit
        
        # Test risk parameters
        self.assertGreater(config.RISK_PERCENT, 0)
        self.assertLess(config.RISK_PERCENT, 10)  # Reasonable risk per trade

def run_tests():
    """Run all tests"""
    print("🧪 Running High-Frequency Scalping EA Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(loader.loadTestsFromTestCase(TestHFScalpingEA))
    test_suite.addTest(loader.loadTestsFromTestCase(TestConfiguration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()
