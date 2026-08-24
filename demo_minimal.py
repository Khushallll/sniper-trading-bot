"""
Minimal Telegram Notification Demo - No Dependencies!
This version works with just the standard library + aiohttp + loguru

Run with: python3 demo_minimal.py
"""

import asyncio
import sys
from datetime import datetime
import ssl

try:
    import aiohttp
    from loguru import logger
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "loguru"])
    import aiohttp
    from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, format="<level>{level: <8}</level> | <level>{message}</level>")


class TelegramNotifierMinimal:
    """Minimal Telegram notifier - no external dependencies"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            # Create SSL context that doesn't verify certificates (for demo purposes)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                url = f"{self.base_url}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        logger.debug(f"✓ Message sent successfully")
                        return True
                    else:
                        logger.error(f"Failed with status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test Telegram connection"""
        message = "✅ <b>Sniper Trading Bot Connected!</b>\n\nNotification system is working correctly."
        return await self.send_message(message)

    async def send_opportunity_alert(self, symbol: str, signal_type: str, entry: float, 
                                     sl: float, tp: float, confidence: float) -> bool:
        """Send opportunity alert"""
        emoji = "🟢" if signal_type == "bullish" else "🔴"
        direction = "📈 BULLISH" if signal_type == "bullish" else "📉 BEARISH"
        message = f"""
{emoji} <b>OPPORTUNITY DETECTED</b> {emoji}

<b>Pair:</b> {symbol}
<b>Signal:</b> {direction}
<b>Confidence:</b> {confidence:.1%}

<b>Entry Price:</b> ${entry:.2f}
<b>Stop Loss:</b> ${sl:.2f}
<b>Take Profit:</b> ${tp:.2f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_trade_execution(self, symbol: str, side: str, qty: float,
                                   entry: float, sl: float, tp: float) -> bool:
        """Send trade execution alert"""
        side_emoji = "🟢 BUY" if side == "buy" else "🔴 SELL"
        message = f"""
{side_emoji} <b>TRADE EXECUTED</b>

<b>Symbol:</b> {symbol}
<b>Quantity:</b> {qty:.4f}

<b>Entry Price:</b> ${entry:.2f}
<b>Stop Loss:</b> ${sl:.2f}
<b>Take Profit:</b> ${tp:.2f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_trade_closed(self, symbol: str, side: str, entry: float, 
                               exit_price: float, qty: float, pnl: float) -> bool:
        """Send trade closed alert"""
        pnl_emoji = "💰" if pnl > 0 else "💸"
        pnl_type = "PROFIT" if pnl > 0 else "LOSS"
        message = f"""
{pnl_emoji} <b>TRADE CLOSED - {pnl_type}</b>

<b>Symbol:</b> {symbol}
<b>Side:</b> {side.upper()}

<b>Entry Price:</b> ${entry:.2f}
<b>Exit Price:</b> ${exit_price:.2f}
<b>Quantity:</b> {qty:.4f}

<b>Performance:</b>
• PnL: ${pnl:+.2f}
• Return: {((exit_price - entry) / entry * 100):+.2f}%

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_daily_summary(self, total: int, wins: int, losses: int, pnl: float) -> bool:
        """Send daily summary"""
        win_rate = wins / total if total > 0 else 0
        pnl_emoji = "📈" if pnl > 0 else "📉"
        message = f"""
{pnl_emoji} <b>DAILY TRADING SUMMARY</b>

<b>Total Trades:</b> {total}
<b>Winning Trades:</b> {wins} ✅
<b>Losing Trades:</b> {losses} ❌
<b>Win Rate:</b> {win_rate:.1%}

<b>Total PnL:</b> ${pnl:+.2f}

<i>Date: {datetime.now().strftime('%Y-%m-%d UTC')}</i>
"""
        return await self.send_message(message)

    async def send_error_alert(self, error_type: str, message_text: str) -> bool:
        """Send error alert"""
        message = f"""
⚠️ <b>ERROR ALERT</b> ⚠️

<b>Error Type:</b> {error_type}
<b>Message:</b> {message_text}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)

    async def send_status_update(self, status: str, positions: int, balance: float, pnl: float) -> bool:
        """Send status update"""
        status_emoji = "🟢" if status == "running" else "🔴"
        pnl_emoji = "📈" if pnl > 0 else "📉"
        message = f"""
{status_emoji} <b>BOT STATUS UPDATE</b>

<b>Status:</b> {status.upper()}
<b>Active Positions:</b> {positions}
<b>Account Balance:</b> ${balance:,.2f}
<b>Daily PnL:</b> {pnl_emoji} ${pnl:+,.2f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return await self.send_message(message)


async def run_demo():
    """Run the minimal demo"""
    print("\n╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "SNIPER TRADING BOT - MINIMAL TELEGRAM DEMO".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝\n")

    # Initialize notifier with your credentials
    notifier = TelegramNotifierMinimal(
        bot_token="8698944043:AAFyQBqO-a1ooEq8KMZby63J7CVvLEz7Ja4",
        chat_id="7650863580"
    )

    # Test connection
    print("🔌 Testing Telegram connection...")
    result = await notifier.test_connection()
    if result:
        print("✅ Telegram connected!\n")
    else:
        print("❌ Connection failed\n")
        print("If you're behind a corporate firewall or proxy, you may need to:")
        print("1. Use a VPN")
        print("2. Configure proxy settings")
        print("3. Check your internet connection\n")
        return

    # Demo 1: Opportunity
    print("📊 DEMO 1: Opportunity Detection")
    print("Sending: Bullish signal for BTC/USDT...\n")
    await notifier.send_opportunity_alert(
        symbol="BTC/USDT",
        signal_type="bullish",
        entry=43250.50,
        sl=42950.00,
        tp=44100.00,
        confidence=0.87
    )
    await asyncio.sleep(1)

    # Demo 2: Trade Execution
    print("📊 DEMO 2: Trade Execution")
    print("Sending: BUY trade executed...\n")
    await notifier.send_trade_execution(
        symbol="BTC/USDT",
        side="buy",
        qty=0.2500,
        entry=43250.50,
        sl=42950.00,
        tp=44100.00
    )
    await asyncio.sleep(1)

    # Demo 3: Trade Closed
    print("📊 DEMO 3: Trade Closed - Profit")
    print("Sending: Trade closed with profit...\n")
    await notifier.send_trade_closed(
        symbol="BTC/USDT",
        side="buy",
        entry=43250.50,
        exit_price=43725.00,
        qty=0.2500,
        pnl=118.69
    )
    await asyncio.sleep(1)

    # Demo 4: Daily Summary
    print("📊 DEMO 4: Daily Summary")
    print("Sending: Daily trading summary...\n")
    await notifier.send_daily_summary(
        total=12,
        wins=10,
        losses=2,
        pnl=1247.50
    )
    await asyncio.sleep(1)

    # Demo 5: Error Alert
    print("📊 DEMO 5: Error Alert")
    print("Sending: Error notification...\n")
    await notifier.send_error_alert(
        error_type="API Connection Error",
        message_text="Connection timeout while fetching market data"
    )
    await asyncio.sleep(1)

    # Demo 6: Status Update
    print("📊 DEMO 6: Status Update")
    print("Sending: Bot status update...\n")
    await notifier.send_status_update(
        status="running",
        positions=3,
        balance=10547.50,
        pnl=547.50
    )

    print("\n" + "="*80)
    print("✅ DEMO COMPLETED!")
    print("="*80)
    print("\n📱 Check your Telegram chat - you should have received 6 messages:")
    print("   1. 🎯 Opportunity Alert")
    print("   2. 🚀 Trade Execution")
    print("   3. 💰 Trade Closed (Profit)")
    print("   4. 📊 Daily Summary")
    print("   5. ⚠️ Error Alert")
    print("   6. 🟢 Status Update\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
