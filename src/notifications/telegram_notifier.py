"""Telegram notification handler for trading alerts"""

import aiohttp
import asyncio
from typing import Optional, Dict
from loguru import logger
from datetime import datetime


class TelegramNotifier:
    """Sends notifications via Telegram"""

    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier

        Args:
            bot_token: Telegram bot token from BotFather
            chat_id: Chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        logger.info(f"Initialized Telegram notifier for chat {chat_id}")

    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a text message to Telegram

        Args:
            message: Message text
            parse_mode: Parse mode (HTML or Markdown)

        Returns:
            True if successful
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": parse_mode
                }
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.debug(f"Telegram message sent successfully")
                        return True
                    else:
                        logger.error(f"Failed to send Telegram message: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_opportunity_alert(self, symbol: str, signal_type: str,
                                    entry_price: float, stop_loss: float,
                                    take_profit: float, confidence: float,
                                    indicators: Dict) -> bool:
        """
        Send trading opportunity alert

        Args:
            symbol: Trading pair
            signal_type: 'bullish' or 'bearish'
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            confidence: Confidence score (0-1)
            indicators: Technical indicators dictionary

        Returns:
            True if successful
        """
        emoji = "🟢" if signal_type == "bullish" else "🔴"
        direction = "📈 BULLISH" if signal_type == "bullish" else "📉 BEARISH"

        message = f"""
{emoji} <b>OPPORTUNITY DETECTED</b> {emoji}

<b>Pair:</b> {symbol}
<b>Signal:</b> {direction}
<b>Confidence:</b> {confidence:.1%}

<b>Entry Price:</b> ${entry_price:.2f}
<b>Stop Loss:</b> ${stop_loss:.2f}
<b>Take Profit:</b> ${take_profit:.2f}

<b>Technical Indicators:</b>
• RSI: {indicators.get('rsi', 'N/A'):.2f}
• MACD: {indicators.get('macd', 'N/A'):.6f}
• ATR: {indicators.get('atr', 'N/A'):.2f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_trade_execution_alert(self, symbol: str, side: str,
                                        quantity: float, entry_price: float,
                                        stop_loss: float, take_profit: float,
                                        risk_amount: float, reward_amount: float,
                                        rr_ratio: float) -> bool:
        """
        Send trade execution alert

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
            True if successful
        """
        side_emoji = "🟢 BUY" if side == "buy" else "🔴 SELL"
        
        message = f"""
{side_emoji} <b>TRADE EXECUTED</b>

<b>Symbol:</b> {symbol}
<b>Side:</b> {side.upper()}
<b>Quantity:</b> {quantity:.4f}

<b>Entry Price:</b> ${entry_price:.2f}
<b>Stop Loss:</b> ${stop_loss:.2f}
<b>Take Profit:</b> ${take_profit:.2f}

<b>Risk Management:</b>
• Risk Amount: ${risk_amount:.2f}
• Reward Amount: ${reward_amount:.2f}
• Risk/Reward Ratio: 1:{rr_ratio:.2f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_trade_closed_alert(self, symbol: str, order_id: str,
                                     side: str, entry_price: float,
                                     exit_price: float, quantity: float,
                                     pnl: float, pnl_percent: float) -> bool:
        """
        Send trade closed alert

        Args:
            symbol: Trading pair
            order_id: Order ID
            side: 'buy' or 'sell'
            entry_price: Entry price
            exit_price: Exit price
            quantity: Quantity
            pnl: Profit/Loss in USD
            pnl_percent: Profit/Loss percentage

        Returns:
            True if successful
        """
        pnl_emoji = "💰" if pnl > 0 else "💸"
        pnl_type = "PROFIT" if pnl > 0 else "LOSS"

        message = f"""
{pnl_emoji} <b>TRADE CLOSED - {pnl_type}</b>

<b>Symbol:</b> {symbol}
<b>Order ID:</b> <code>{order_id}</code>
<b>Side:</b> {side.upper()}

<b>Entry Price:</b> ${entry_price:.2f}
<b>Exit Price:</b> ${exit_price:.2f}
<b>Quantity:</b> {quantity:.4f}

<b>Performance:</b>
• PnL: ${pnl:+.2f}
• Return: {pnl_percent:+.2f}%

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_daily_summary(self, total_trades: int, winning_trades: int,
                                losing_trades: int, total_pnl: float,
                                win_rate: float) -> bool:
        """
        Send daily trading summary

        Args:
            total_trades: Total number of trades
            winning_trades: Number of winning trades
            losing_trades: Number of losing trades
            total_pnl: Total profit/loss
            win_rate: Win rate percentage

        Returns:
            True if successful
        """
        pnl_emoji = "📈" if total_pnl > 0 else "📉"

        message = f"""
{pnl_emoji} <b>DAILY TRADING SUMMARY</b>

<b>Total Trades:</b> {total_trades}
<b>Winning Trades:</b> {winning_trades} ✅
<b>Losing Trades:</b> {losing_trades} ❌
<b>Win Rate:</b> {win_rate:.1%}

<b>Total PnL:</b> ${total_pnl:+.2f}

<i>Date: {datetime.now().strftime('%Y-%m-%d UTC')}</i>
"""
        return await self.send_message(message)

    async def send_error_alert(self, error_type: str, error_message: str,
                              symbol: str = None) -> bool:
        """
        Send error alert

        Args:
            error_type: Type of error
            error_message: Error message
            symbol: Optional trading pair

        Returns:
            True if successful
        """
        symbol_info = f"\n<b>Symbol:</b> {symbol}" if symbol else ""

        message = f"""
⚠️ <b>ERROR ALERT</b> ⚠️

<b>Error Type:</b> {error_type}{symbol_info}
<b>Message:</b> {error_message}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_warning_alert(self, warning_type: str, warning_message: str) -> bool:
        """
        Send warning alert

        Args:
            warning_type: Type of warning
            warning_message: Warning message

        Returns:
            True if successful
        """
        message = f"""
⚠️ <b>WARNING</b> ⚠️

<b>Type:</b> {warning_type}
<b>Message:</b> {warning_message}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_status_update(self, status: str, active_positions: int,
                                account_balance: float, daily_pnl: float) -> bool:
        """
        Send bot status update

        Args:
            status: Bot status ('running', 'paused', 'stopped')
            active_positions: Number of active positions
            account_balance: Current account balance
            daily_pnl: Daily profit/loss

        Returns:
            True if successful
        """
        status_emoji = "🟢" if status == "running" else "🟡" if status == "paused" else "🔴"
        pnl_emoji = "📈" if daily_pnl > 0 else "📉"

        message = f"""
{status_emoji} <b>BOT STATUS UPDATE</b>

<b>Status:</b> {status.upper()}
<b>Active Positions:</b> {active_positions}
<b>Account Balance:</b> ${account_balance:,.2f}
<b>Daily PnL:</b> {pnl_emoji} ${daily_pnl:+,.2f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def test_connection(self) -> bool:
        """
        Test Telegram connection

        Returns:
            True if connection is successful
        """
        try:
            message = "✅ <b>Sniper Trading Bot Connected!</b>\n\nNotification system is working correctly."
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
