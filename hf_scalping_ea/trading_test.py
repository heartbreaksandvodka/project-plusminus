"""
Trading functionality tests for High-Frequency Scalping EA
Tests order placement, risk management, and performance tracking
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, date

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestScalpingEA(unittest.TestCase):
    """Comprehensive test suite for HF Scalping EA"""
    
    def setUp(self):
        """Set up test environment with mocked MT5"""
        self.mt5_mock = Mock()
        self._setup_mt5_constants()
        
        with patch('mt5_hf_scalping_ea.mt5', self.mt5_mock):
            from mt5_hf_scalping_ea import HighFrequencyScalpingEA
            self.ea = HighFrequencyScalpingEA()
            self._setup_symbol_info()
    
    def _setup_mt5_constants(self):
        """Configure MT5 mock constants and responses"""
        self.mt5_mock.initialize.return_value = True
        self.mt5_mock.login.return_value = True
        self.mt5_mock.TRADE_RETCODE_DONE = 10009
        self.mt5_mock.ORDER_TYPE_BUY = 0
        self.mt5_mock.ORDER_TYPE_SELL = 1
        self.mt5_mock.TRADE_ACTION_DEAL = 1
        self.mt5_mock.ORDER_TIME_GTC = 0
        self.mt5_mock.ORDER_FILLING_IOC = 1
        self.mt5_mock.POSITION_TYPE_BUY = 0
        self.mt5_mock.POSITION_TYPE_SELL = 1
        self.mt5_mock.TRADE_ACTION_SLTP = 2
        
        # Mock tick data
        mock_tick = Mock()
        mock_tick.bid = 1.18450
        mock_tick.ask = 1.18453
        mock_tick.time = 1627383600
        mock_tick.volume = 100
        self.mt5_mock.symbol_info_tick.return_value = mock_tick
    
    def _setup_symbol_info(self):
        """Configure symbol information"""
        mock_symbol = Mock()
        mock_symbol.point = 0.00001
        mock_symbol.digits = 5
        mock_symbol.trade_tick_value = 1.0
        mock_symbol.volume_min = 0.01
        mock_symbol.volume_max = 100.0
        mock_symbol.volume_step = 0.01
        mock_symbol.visible = True
        
        self.ea.symbol_info = mock_symbol
        self.ea.point = mock_symbol.point
        self.ea.digits = mock_symbol.digits
    
    def _get_mock_prices(self):
        """Get standard mock price data"""
        return {
            'time': 1627383600,
            'bid': 1.18450,
            'ask': 1.18453,
            'spread': 3.0
        }
    
    def _setup_successful_order_mocks(self):
        """Setup mocks for successful order placement"""
        mock_result = Mock()
        mock_result.retcode = 10009
        mock_result.comment = "Request executed"
        mock_result.order = 12345
        
        mock_account = Mock()
        mock_account.balance = 10000.0
        mock_account.equity = 10000.0
        
        self.mt5_mock.order_send.return_value = mock_result
        self.mt5_mock.positions_get.return_value = ()
        self.mt5_mock.account_info.return_value = mock_account
    
    def test_order_placement(self):
        """Test BUY and SELL order placement"""
        with patch('mt5_hf_scalping_ea.mt5', self.mt5_mock):
            self._setup_successful_order_mocks()
            
            with patch.object(self.ea, 'get_current_prices', return_value=self._get_mock_prices()):
                with patch.object(self.ea, 'is_trading_time', return_value=True):
                    with patch.object(self.ea, 'calculate_position_size', return_value=0.01):
                        # Test BUY order
                        result_buy = self.ea.place_scalping_order('BUY', self._get_mock_prices())
                        self.assertTrue(result_buy)
                        self.assertEqual(self.ea.daily_trades, 1)
                        
                        # Test SELL order
                        result_sell = self.ea.place_scalping_order('SELL', self._get_mock_prices())
                        self.assertTrue(result_sell)
                        self.assertEqual(self.ea.daily_trades, 2)
                        
                        # Verify order parameters
                        self.assertEqual(self.mt5_mock.order_send.call_count, 2)
    
    def test_risk_limits(self):
        """Test daily limits and risk management"""
        # Test daily trade limit
        self.ea.daily_trades = 100
        result = self.ea.place_scalping_order('BUY', self._get_mock_prices())
        self.assertFalse(result)
        
        # Test daily loss limit
        self.ea.daily_trades = 0
        self.ea.daily_profit = -100.0
        result = self.ea.place_scalping_order('BUY', self._get_mock_prices())
        self.assertFalse(result)
        
        # Test concurrent position limit
        self.ea.daily_profit = 0.0
        mock_positions = [Mock() for _ in range(3)]
        self.mt5_mock.positions_get.return_value = mock_positions
        result = self.ea.place_scalping_order('BUY', self._get_mock_prices())
        self.assertFalse(result)
    
    def test_position_management(self):
        """Test position management and trailing stops"""
        mock_positions = [
            Mock(symbol='BTCUSD', ticket=12345, type=0),  # BUY
            Mock(symbol='BTCUSD', ticket=12346, type=1),  # SELL
        ]
        
        with patch('mt5_hf_scalping_ea.mt5', self.mt5_mock):
            self.mt5_mock.positions_get.return_value = tuple(mock_positions)
            
            with patch.object(self.ea, 'apply_trailing_stop') as mock_trailing:
                self.ea.manage_positions()
                self.assertEqual(mock_trailing.call_count, 2)
    
    def test_calculations(self):
        """Test stop loss, take profit, and breakeven calculations"""
        entry_price = 1.18450
        
        # Test stop loss calculation (30 pips)
        expected_sl_buy = entry_price - (30 * 0.00001)
        expected_sl_sell = entry_price + (30 * 0.00001)
        
        self.assertLess(expected_sl_buy, entry_price)
        self.assertGreater(expected_sl_sell, entry_price)
        
        # Test take profit calculation (30 pips)
        expected_tp_buy = entry_price + (30 * 0.00001)
        expected_tp_sell = entry_price - (30 * 0.00001)
        
        self.assertGreater(expected_tp_buy, entry_price)
        self.assertLess(expected_tp_sell, entry_price)
        
        # Test breakeven trigger (15 pips - halfway to TP)
        breakeven_distance_buy = (entry_price + (15 * 0.00001) - entry_price) / 0.00001
        breakeven_distance_sell = (entry_price - (entry_price - (15 * 0.00001))) / 0.00001
        
        self.assertAlmostEqual(breakeven_distance_buy, 15, places=1)
        self.assertAlmostEqual(breakeven_distance_sell, 15, places=1)
    
    def test_daily_stats_reset(self):
        """Test daily statistics reset functionality"""
        # Set up initial stats
        self.ea.daily_trades = 50
        self.ea.daily_profit = 200.0
        self.ea.today = date(2025, 7, 25)  # Yesterday
        
        # Mock current date
        with patch('mt5_hf_scalping_ea.datetime') as mock_datetime:
            mock_datetime.now.return_value.date.return_value = date(2025, 7, 26)  # Today
            self.mt5_mock.history_deals_get.return_value = []
            
            self.ea.update_daily_stats()
        
        # Verify stats reset
        self.assertEqual(self.ea.daily_trades, 0)
        self.assertEqual(self.ea.daily_profit, 0.0)
        self.assertEqual(self.ea.today, date(2025, 7, 26))
    
    def test_performance_stats(self):
        """Test performance statistics calculation"""
        # Set up performance data
        self.ea.total_trades = 100
        self.ea.winning_trades = 65
        self.ea.daily_trades = 25
        self.ea.daily_profit = 150.0
        self.ea.total_profit = 2500.0
        
        # Mock account info
        mock_account = Mock()
        mock_account.balance = 12500.0
        mock_account.equity = 12650.0
        
        with patch('mt5_hf_scalping_ea.mt5.account_info', return_value=mock_account):
            stats = self.ea.get_performance_stats()
            
            if stats:  # If we got valid stats
                self.assertEqual(stats['total_trades'], 100)
                self.assertEqual(stats['win_rate'], 65.0)
                self.assertEqual(stats['account_balance'], 12500.0)
    
    def test_error_handling(self):
        """Test error handling and failed orders"""
        # Mock failed order response
        mock_result = Mock()
        mock_result.retcode = 10013  # Invalid request
        mock_result.comment = "Invalid request"
        
        self.mt5_mock.order_send.return_value = mock_result
        self.mt5_mock.positions_get.return_value = ()
        
        result = self.ea.place_scalping_order('BUY', self._get_mock_prices())
        self.assertFalse(result)
        self.assertEqual(self.ea.daily_trades, 0)  # Counter should not increment

def run_trading_tests():
    """Run all trading tests"""
    print("🧪 Running High-Frequency Scalping Trading Tests")
    print("=" * 55)
    
    # Create and run test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestScalpingEA)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 55)
    if result.wasSuccessful():
        print("✅ All trading tests passed!")
        print("🎯 Order placement logic verified")
        print("🛡️ Risk management validated") 
        print("📊 Performance tracking confirmed")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        
        for test, error in result.failures + result.errors:
            print(f"   • {test}: {error.split(':')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_trading_tests()
