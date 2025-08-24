from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Sum, Count, Q, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import AlgorithmExecution, TradeResult, AlgorithmSignal, MT5Account
from ..serializers import AlgorithmExecutionSerializer, TradeResultSerializer, AlgorithmSignalSerializer
from ..api_views.mt5_authentication_views import get_mt5_account
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_algorithm_status(request, execution_id):
    """Get detailed real-time status of a running algorithm"""
    try:
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=400)
        
        execution = get_object_or_404(AlgorithmExecution, id=execution_id, mt5_account=account)
        
        # Get recent trades
        recent_trades = execution.trade_results.filter(
            opened_at__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-opened_at')[:10]
        
        # Get recent signals
        recent_signals = execution.signals.filter(
            generated_at__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-generated_at')[:10]
        
        # Calculate performance metrics
        all_trades = execution.trade_results.filter(trade_status='closed')
        performance_stats = calculate_performance_metrics(all_trades)
        
        # Real-time status
        real_time_status = {
            'is_running': execution.execution_status == 'running',
            'current_pnl': float(execution.profit_loss),
            'positions_count': execution.positions_count,
            'last_trade_time': execution.last_trade_time.isoformat() if execution.last_trade_time else None,
            'last_heartbeat': execution.last_heartbeat.isoformat() if execution.last_heartbeat else None,
            'error_message': execution.error_message,
            'daily_pnl': float(execution.daily_pnl),
            'current_drawdown': float(execution.current_drawdown),
            'max_drawdown': float(execution.max_drawdown)
        }
        
        return Response({
            'execution': AlgorithmExecutionSerializer(execution).data,
            'real_time_status': real_time_status,
            'performance_metrics': performance_stats,
            'recent_trades': TradeResultSerializer(recent_trades, many=True).data,
            'recent_signals': AlgorithmSignalSerializer(recent_signals, many=True).data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting algorithm status: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_algorithm_analytics(request, execution_id):
    """Get detailed analytics for an algorithm execution"""
    try:
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=400)
        
        execution = get_object_or_404(AlgorithmExecution, id=execution_id, mt5_account=account)
        
        # Time range filter
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get trades in time range
        trades = execution.trade_results.filter(
            opened_at__gte=start_date,
            trade_status='closed'
        )
        
        # Calculate detailed analytics
        analytics = {
            'overview': calculate_performance_metrics(trades),
            'daily_performance': calculate_daily_performance(trades, days),
            'trade_distribution': calculate_trade_distribution(trades),
            'symbol_performance': calculate_symbol_performance(trades),
            'risk_metrics': calculate_risk_metrics(trades, execution),
            'signal_analytics': calculate_signal_analytics(execution, start_date)
        }
        
        return Response(analytics)
        
    except Exception as e:
        logger.error(f"Error getting algorithm analytics: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trade_history(request, execution_id):
    """Get paginated trade history for an algorithm"""
    try:
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=400)
        
        execution = get_object_or_404(AlgorithmExecution, id=execution_id, mt5_account=account)
        
        # Pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        
        # Filters
        symbol = request.GET.get('symbol')
        trade_type = request.GET.get('trade_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Build query
        trades = execution.trade_results.all()
        
        if symbol:
            trades = trades.filter(symbol=symbol)
        if trade_type:
            trades = trades.filter(trade_type=trade_type)
        if start_date:
            trades = trades.filter(opened_at__gte=start_date)
        if end_date:
            trades = trades.filter(opened_at__lte=end_date)
        
        # Pagination
        total_trades = trades.count()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_trades = trades.order_by('-opened_at')[start_idx:end_idx]
        
        return Response({
            'trades': TradeResultSerializer(paginated_trades, many=True).data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_trades': total_trades,
                'total_pages': (total_trades + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting trade history: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_algorithm_config(request, execution_id):
    """Update algorithm configuration in real-time"""
    try:
        account, error = get_mt5_account(request.user)
        if error:
            return Response(error, status=400)
        
        execution = get_object_or_404(AlgorithmExecution, id=execution_id, mt5_account=account)
        
        # Get configuration updates
        config_updates = request.data.get('config', {})
        
        # Update execution performance metrics if provided
        if 'performance_metrics' in config_updates:
            execution.performance_metrics.update(config_updates['performance_metrics'])
        
        # Save changes
        execution.save()
        
        # Broadcast configuration update via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        group_name = f'algorithm_{execution_id}'
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'config_update',
                'message': {
                    'type': 'config_update',
                    'execution_id': execution_id,
                    'config_updates': config_updates,
                    'timestamp': timezone.now().isoformat()
                }
            }
        )
        
        return Response({
            'message': 'Configuration updated successfully',
            'execution': AlgorithmExecutionSerializer(execution).data
        })
        
    except Exception as e:
        logger.error(f"Error updating algorithm config: {str(e)}")
        return Response({'error': str(e)}, status=500)


# Helper functions for analytics calculations

def calculate_performance_metrics(trades):
    """Calculate comprehensive performance metrics"""
    if not trades.exists():
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'avg_trade_duration': 0
        }
    
    # Basic statistics
    total_trades = trades.count()
    winning_trades = trades.filter(profit_loss__gt=0).count()
    losing_trades = trades.filter(profit_loss__lt=0).count()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # P&L statistics
    total_pnl = trades.aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0
    avg_win = trades.filter(profit_loss__gt=0).aggregate(Avg('profit_loss'))['profit_loss__avg'] or 0
    avg_loss = trades.filter(profit_loss__lt=0).aggregate(Avg('profit_loss'))['profit_loss__avg'] or 0
    
    # Profit factor
    total_wins = trades.filter(profit_loss__gt=0).aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0
    total_losses = abs(trades.filter(profit_loss__lt=0).aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0)
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    # Extremes
    largest_win = trades.aggregate(Max('profit_loss'))['profit_loss__max'] or 0
    largest_loss = trades.aggregate(Min('profit_loss'))['profit_loss__min'] or 0
    
    # Average trade duration
    avg_duration = trades.exclude(duration_seconds__isnull=True).aggregate(
        Avg('duration_seconds'))['duration_seconds__avg'] or 0
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 2),
        'total_pnl': float(total_pnl),
        'avg_win': float(avg_win),
        'avg_loss': float(avg_loss),
        'profit_factor': round(profit_factor, 2),
        'largest_win': float(largest_win),
        'largest_loss': float(largest_loss),
        'avg_trade_duration': round(avg_duration / 60, 2) if avg_duration else 0  # in minutes
    }


def calculate_daily_performance(trades, days):
    """Calculate daily performance over specified period"""
    daily_data = []
    start_date = timezone.now() - timedelta(days=days)
    
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_trades = trades.filter(
            closed_at__gte=day_start,
            closed_at__lt=day_end
        )
        
        daily_pnl = day_trades.aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0
        trade_count = day_trades.count()
        
        daily_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'pnl': float(daily_pnl),
            'trade_count': trade_count
        })
    
    return daily_data


def calculate_trade_distribution(trades):
    """Calculate trade distribution by various metrics"""
    # By hour
    hourly_distribution = []
    for hour in range(24):
        hour_trades = trades.filter(opened_at__hour=hour).count()
        hourly_distribution.append({
            'hour': hour,
            'count': hour_trades
        })
    
    # By symbol
    symbol_distribution = trades.values('symbol').annotate(
        count=Count('id'),
        total_pnl=Sum('profit_loss')
    ).order_by('-count')
    
    return {
        'hourly': hourly_distribution,
        'by_symbol': list(symbol_distribution)
    }


def calculate_symbol_performance(trades):
    """Calculate performance metrics by symbol"""
    symbol_stats = trades.values('symbol').annotate(
        total_trades=Count('id'),
        winning_trades=Count('id', filter=Q(profit_loss__gt=0)),
        total_pnl=Sum('profit_loss'),
        avg_pnl=Avg('profit_loss')
    ).order_by('-total_pnl')
    
    # Calculate win rate for each symbol
    for stat in symbol_stats:
        stat['win_rate'] = (stat['winning_trades'] / stat['total_trades'] * 100) if stat['total_trades'] > 0 else 0
        stat['total_pnl'] = float(stat['total_pnl'])
        stat['avg_pnl'] = float(stat['avg_pnl'])
    
    return list(symbol_stats)


def calculate_risk_metrics(trades, execution):
    """Calculate risk-related metrics"""
    if not trades.exists():
        return {}
    
    # Calculate drawdown series
    running_balance = 0
    peak_balance = 0
    max_drawdown = 0
    drawdown_series = []
    
    for trade in trades.order_by('closed_at'):
        running_balance += float(trade.profit_loss)
        peak_balance = max(peak_balance, running_balance)
        current_drawdown = peak_balance - running_balance
        max_drawdown = max(max_drawdown, current_drawdown)
        
        drawdown_series.append({
            'date': trade.closed_at.isoformat(),
            'balance': running_balance,
            'drawdown': current_drawdown
        })
    
    return {
        'max_drawdown': max_drawdown,
        'current_drawdown': float(execution.current_drawdown),
        'drawdown_series': drawdown_series[-100:],  # Last 100 points
        'risk_violations': execution.risk_violations
    }


def calculate_signal_analytics(execution, start_date):
    """Calculate signal generation and execution analytics"""
    signals = execution.signals.filter(generated_at__gte=start_date)
    
    if not signals.exists():
        return {}
    
    total_signals = signals.count()
    executed_signals = signals.filter(signal_status='executed').count()
    failed_signals = signals.filter(signal_status='failed').count()
    
    # Signal type distribution
    signal_types = signals.values('signal_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Signal execution rate
    execution_rate = (executed_signals / total_signals * 100) if total_signals > 0 else 0
    
    return {
        'total_signals': total_signals,
        'executed_signals': executed_signals,
        'failed_signals': failed_signals,
        'execution_rate': round(execution_rate, 2),
        'signal_distribution': list(signal_types)
    }
