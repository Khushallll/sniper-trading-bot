"""Central notification manager for coordinating alerts"""

import asyncio
from typing import Optional, Dict, List
from loguru import logger
from src.notifications.telegram_notifier import TelegramNotifier


class NotificationManager:
    """Manages all notifications across different channels"""

    def __init__(self, config: Dict):
        """
        Initialize notification manager

        Args:
            config: Configuration dictionary with notification settings
        """
        self.config = config
        self.telegram_notifier = None
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.enabled_channels = []
        
        # Initialize Telegram if configured
        if config.get('telegram', {}).get('enabled', False):
            bot_token = config['telegram'].get('bot_token')
            chat_id = config['telegram'].get('chat_id')
            
            if bot_token and chat_id:
                self.telegram_notifier = TelegramNotifier(bot_token, chat_id)
                self.enabled_channels.append('telegram')
                logger.info("Telegram notifications enabled")
            else:
                logger.warning("Telegram enabled but bot_token or chat_id missing")
        
        logger.info(f"Notification manager initialized with channels: {self.enabled_channels}")

    async def test_notifications(self) -> bool:
        """
        Test all notification channels

        Returns:
            True if all channels are working
        """
        logger.info("Testing notification channels...")
        all_working = True
        
        if self.telegram_notifier:
            result = await self.telegram_notifier.test_connection()
            if result:
                logger.info("✓ Telegram connection test passed")
            else:
                logger.error("✗ Telegram connection test failed")
                all_working = False
        
        return all_working

    async def notify_opportunity(self, opportunity) -> bool:
        """
        Notify about detected trading opportunity

        Args:
            opportunity: TradingOpportunity object

        Returns:
            True if notification sent successfully
        """
        tasks = []
        
        if self.telegram_notifier:
            tasks.append(self.telegram_notifier.send_opportunity_alert(
                symbol=opportunity.symbol,
                signal_type=opportunity.signal_type,
                entry_price=opportunity.entry_price,
                stop_loss=opportunity.stop_loss,
                take_profit=opportunity.take_profit,
                confidence=opportunity.confidence_score,
                indicators=opportunity.indicators
            ))
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks)
        return any(results)

    async def notify_trade_executed(self, symbol: str, side: str, quantity: float,
                                   entry_price: float, stop_loss: float,
                                   take_profit: float, risk_amount: float,
                                   reward_amount: float, rr_ratio: float) -> bool:
        """
        Notify about trade execution

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            quantity: Order quantity
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            risk_amount: Risk amount in USD
            reward_amount: Reward amount in USD
            rr_ratio: Risk/reward ratio

        Returns:
            True if notification sent successfully
        """
        tasks = []
        
        if self.telegram_notifier:
            tasks.append(self.telegram_notifier.send_trade_execution_alert(
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                reward_amount=reward_amount,
                rr_ratio=rr_ratio
            ))
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks)
        return any(results)

    async def notify_trade_closed(self, symbol: str, order_id: str, side: str,
                                 entry_price: float, exit_price: float,
                                 quantity: float, pnl: float) -> bool:
        """
        Notify about closed trade

        Args:
            symbol: Trading pair
            order_id: Order ID
            side: 'buy' or 'sell'
            entry_price: Entry price
            exit_price: Exit price
            quantity: Quantity
            pnl: Profit/Loss in USD

        Returns:
            True if notification sent successfully
        """
        pnl_percent = ((exit_price - entry_price) / entry_price * 100) if side == 'buy' else ((entry_price - exit_price) / entry_price * 100)
        
        tasks = []
        
        if self.telegram_notifier:
            tasks.append(self.telegram_notifier.send_trade_closed_alert(
                symbol=symbol,
                order_id=order_id,
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                pnl=pnl,
                pnl_percent=pnl_percent
            ))
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks)
        return any(results)

    async def notify_daily_summary(self, total_trades: int, winning_trades: int,
                                  losing_trades: int, total_pnl: float) -> bool:
        """
        Notify daily trading summary

        Args:
            total_trades: Total number of trades
            winning_trades: Number of winning trades
            losing_trades: Number of losing trades
            total_pnl: Total profit/loss

        Returns:
            True if notification sent successfully
        """
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        tasks = []
        
        if self.telegram_notifier:
            tasks.append(self.telegram_notifier.send_daily_summary(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                total_pnl=total_pnl,
                win_rate=win_rate
            ))
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks)
        return any(results)

    async def notify_error(self, error_type: str, error_message: str,
                          symbol: str = None) -> bool:
        """
        Notify about errors

        Args:
            error_type: Type of error
            error_message: Error message
            symbol: Optional trading pair

        Returns:
            True if notification sent successfully
        """
        tasks = []
        
        if self.telegram_notifier:
            tasks.append(self.telegram_notifier.send_error_alert(
                error_type=error_type,
                error_message=error_message,
                symbol=symbol
            ))
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks)
        return any(results)

    async def notify_warning(self, warning_type: str, warning_message: str) -> bool:
        """
        Notify about warnings

        Args:
            warning_type: Type of warning
            warning_message: Warning message

        Returns:
            True if notification sent successfully
        """
        tasks = []
        
        if self.telegram_notifier:
            tasks.append(self.telegram_notifier.send_warning_alert(
                warning_type=warning_type,
                warning_message=warning_message
            ))
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks)
        return any(results)

    async def notify_status_update(self, status: str, active_positions: int,
                                  account_balance: float, daily_pnl: float) -> bool:
        """
        Notify bot status update

        Args:
            status: Bot status ('running', 'paused', 'stopped')
            active_positions: Number of active positions
            account_balance: Current account balance
            daily_pnl: Daily profit/loss

        Returns:
            True if notification sent successfully
        """
        tasks = []
        
        if self.telegram_notifier:
            tasks.append(self.telegram_notifier.send_status_update(
                status=status,
                active_positions=active_positions,
                account_balance=account_balance,
                daily_pnl=daily_pnl
            ))
        
        if not tasks:
            return False
        
        results = await asyncio.gather(*tasks)
        return any(results)
