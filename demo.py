"""
Demo script to showcase Sniper Trading Bot with Telegram notifications

This script simulates the bot detecting opportunities and sending
real Telegram notifications to show you how the system works.

Run with: python demo.py
"""

import asyncio
import sys
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

from src.notifications.notification_manager import NotificationManager
from src.detection.opportunity_detector import OpportunityDetector, TradingOpportunity
from src.risk_management.risk_manager import RiskManager


def create_sample_ohlcv(trend="bullish"):
    """Create sample OHLCV data for demonstration"""
    dates = pd.date_range('2024-01-01', periods=100, freq='1h')
    
    if trend == "bullish":
        # Create uptrend
        base_price = 43000
        prices = base_price + np.cumsum(np.random.uniform(-5, 15, 100))
    else:
        # Create downtrend
        base_price = 43000
        prices = base_price - np.cumsum(np.random.uniform(-5, 15, 100))
    
    data = {
        'open': prices + np.random.uniform(-50, 50, 100),
        'high': prices + np.random.uniform(50, 150, 100),
        'low': prices - np.random.uniform(50, 150, 100),
        'close': prices,
        'volume': np.random.uniform(5000000, 15000000, 100)
    }
    
    df = pd.DataFrame(data, index=dates)
    return df


async def demo_opportunity_detection():
    """Demo: Detect trading opportunities and send alerts"""
    print("\n" + "="*80)
    print("DEMO 1: OPPORTUNITY DETECTION WITH TELEGRAM ALERTS")
    print("="*80 + "\n")
    
    # Initialize notification manager
    config = {
        "telegram": {
            "enabled": True,
            "bot_token": "8698944043:AAFyQBqO-a1ooEq8KMZby63J7CVvLEz7Ja4",
            "chat_id": "7650863580"
        }
    }
    
    notif_manager = NotificationManager(config)
    
    # Test Telegram connection
    print("🔌 Testing Telegram connection...")
    result = await notif_manager.test_notifications()
    if result:
        print("✅ Telegram connected successfully!\n")
    else:
        print("❌ Telegram connection failed\n")
        return
    
    # Create opportunity detector
    detection_config = {
        'min_volume_threshold': 1000000,
        'price_change_threshold': 0.02,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'macd_signal_threshold': 0.0001
    }
    detector = OpportunityDetector(detection_config)
    
    # Demo bullish opportunity
    print("📊 Analyzing market data for BTC/USDT...")
    ohlcv = create_sample_ohlcv(trend="bullish")
    
    print("🎯 Simulating opportunity detection...\n")
    
    # Create mock opportunity
    opportunity = TradingOpportunity(
        symbol="BTC/USDT",
        timestamp=datetime.now(),
        entry_price=43250.50,
        stop_loss=42950.00,
        take_profit=44100.00,
        confidence_score=0.87,
        signal_type="bullish",
        indicators={
            'rsi': 65.32,
            'macd': 0.000234,
            'atr': 180.50
        },
        reasoning="Strong bullish momentum with RSI above 60 and MACD crossover"
    )
    
    print(f"🟢 OPPORTUNITY DETECTED!")
    print(f"   Pair: {opportunity.symbol}")
    print(f"   Signal: {opportunity.signal_type.upper()}")
    print(f"   Entry: ${opportunity.entry_price:.2f}")
    print(f"   Stop Loss: ${opportunity.stop_loss:.2f}")
    print(f"   Take Profit: ${opportunity.take_profit:.2f}")
    print(f"   Confidence: {opportunity.confidence_score:.1%}\n")
    
    print("📤 Sending Telegram notification...\n")
    await notif_manager.notify_opportunity(opportunity)
    
    print("✅ Opportunity alert sent to Telegram!\n")


async def demo_trade_execution():
    """Demo: Send trade execution alerts"""
    print("\n" + "="*80)
    print("DEMO 2: TRADE EXECUTION ALERTS")
    print("="*80 + "\n")
    
    config = {
        "telegram": {
            "enabled": True,
            "bot_token": "8698944043:AAFyQBqO-a1ooEq8KMZby63J7CVvLEz7Ja4",
            "chat_id": "7650863580"
        }
    }
    
    notif_manager = NotificationManager(config)
    
    print("🚀 Simulating trade execution...\n")
    
    print(f"🟢 BUY TRADE EXECUTED")
    print(f"   Symbol: BTC/USDT")
    print(f"   Quantity: 0.2500 BTC")
    print(f"   Entry Price: $43,250.50")
    print(f"   Stop Loss: $42,950.00")
    print(f"   Take Profit: $44,100.00")
    print(f"   Risk Amount: $125.00")
    print(f"   Reward Amount: $425.00")
    print(f"   Risk/Reward Ratio: 1:3.4\n")
    
    print("📤 Sending trade execution notification...\n")
    
    await notif_manager.notify_trade_executed(
        symbol="BTC/USDT",
        side="buy",
        quantity=0.2500,
        entry_price=43250.50,
        stop_loss=42950.00,
        take_profit=44100.00,
        risk_amount=125.00,
        reward_amount=425.00,
        rr_ratio=3.4
    )
    
    print("✅ Trade execution alert sent to Telegram!\n")


async def demo_trade_closed():
    """Demo: Send trade closed alerts with P&L"""
    print("\n" + "="*80)
    print("DEMO 3: TRADE CLOSED - PROFIT ALERT")
    print("="*80 + "\n")
    
    config = {
        "telegram": {
            "enabled": True,
            "bot_token": "8698944043:AAFyQBqO-a1ooEq8KMZby63J7CVvLEz7Ja4",
            "chat_id": "7650863580"
        }
    }
    
    notif_manager = NotificationManager(config)
    
    print("💰 Simulating trade closure with profit...\n")
    
    entry_price = 43250.50
    exit_price = 43725.00
    quantity = 0.2500
    pnl = (exit_price - entry_price) * quantity
    
    print(f"💰 TRADE CLOSED - PROFIT")
    print(f"   Symbol: BTC/USDT")
    print(f"   Order ID: ORDER_2024080112345")
    print(f"   Side: BUY")
    print(f"   Entry: $43,250.50")
    print(f"   Exit: $43,725.00")
    print(f"   Quantity: 0.2500 BTC")
    print(f"   P&L: +${pnl:.2f}")
    print(f"   Return: +1.10%\n")
    
    print("📤 Sending trade closed notification...\n")
    
    await notif_manager.notify_trade_closed(
        symbol="BTC/USDT",
        order_id="ORDER_2024080112345",
        side="buy",
        entry_price=entry_price,
        exit_price=exit_price,
        quantity=quantity,
        pnl=pnl
    )
    
    print("✅ Trade closed alert sent to Telegram!\n")


async def demo_daily_summary():
    """Demo: Send daily trading summary"""
    print("\n" + "="*80)
    print("DEMO 4: DAILY TRADING SUMMARY")
    print("="*80 + "\n")
    
    config = {
        "telegram": {
            "enabled": True,
            "bot_token": "8698944043:AAFyQBqO-a1ooEq8KMZby63J7CVvLEz7Ja4",
            "chat_id": "7650863580"
        }
    }
    
    notif_manager = NotificationManager(config)
    
    print("📊 Simulating end-of-day summary...\n")
    
    total_trades = 12
    winning_trades = 10
    losing_trades = 2
    total_pnl = 1247.50
    win_rate = winning_trades / total_trades
    
    print(f"📊 DAILY TRADING SUMMARY")
    print(f"   Total Trades: {total_trades}")
    print(f"   Winning Trades: {winning_trades} ✅")
    print(f"   Losing Trades: {losing_trades} ❌")
    print(f"   Win Rate: {win_rate:.1%}")
    print(f"   Total P&L: +${total_pnl:.2f}\n")
    
    print("📤 Sending daily summary notification...\n")
    
    await notif_manager.notify_daily_summary(
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        total_pnl=total_pnl
    )
    
    print("✅ Daily summary sent to Telegram!\n")


async def demo_error_alert():
    """Demo: Send error alerts"""
    print("\n" + "="*80)
    print("DEMO 5: ERROR AND WARNING ALERTS")
    print("="*80 + "\n")
    
    config = {
        "telegram": {
            "enabled": True,
            "bot_token": "8698944043:AAFyQBqO-a1ooEq8KMZby63J7CVvLEz7Ja4",
            "chat_id": "7650863580"
        }
    }
    
    notif_manager = NotificationManager(config)
    
    print("⚠️ Simulating error alert...\n")
    
    print(f"⚠️ ERROR ALERT")
    print(f"   Type: API Connection Error")
    print(f"   Symbol: ETH/USDT")
    print(f"   Message: Connection timeout while fetching market data\n")
    
    print("📤 Sending error notification...\n")
    
    await notif_manager.notify_error(
        error_type="API Connection Error",
        error_message="Connection timeout while fetching market data",
        symbol="ETH/USDT"
    )
    
    print("✅ Error alert sent to Telegram!\n")
    
    # Warning alert
    print("⚠️ Simulating warning alert...\n")
    
    print(f"⚠️ WARNING")
    print(f"   Type: Trade Validation Failed")
    print(f"   Message: Trade rejected - Risk/Reward ratio below minimum threshold\n")
    
    print("📤 Sending warning notification...\n")
    
    await notif_manager.notify_warning(
        warning_type="Trade Validation Failed",
        warning_message="Trade rejected - Risk/Reward ratio below minimum threshold"
    )
    
    print("✅ Warning alert sent to Telegram!\n")


async def demo_status_update():
    """Demo: Send status updates"""
    print("\n" + "="*80)
    print("DEMO 6: BOT STATUS UPDATE")
    print("="*80 + "\n")
    
    config = {
        "telegram": {
            "enabled": True,
            "bot_token": "8698944043:AAFyQBqO-a1ooEq8KMZby63J7CVvLEz7Ja4",
            "chat_id": "7650863580"
        }
    }
    
    notif_manager = NotificationManager(config)
    
    print("🟢 Simulating bot status update...\n")
    
    print(f"🟢 BOT STATUS UPDATE")
    print(f"   Status: RUNNING")
    print(f"   Active Positions: 3")
    print(f"   Account Balance: $10,547.50")
    print(f"   Daily P&L: +$547.50\n")
    
    print("📤 Sending status update...\n")
    
    await notif_manager.notify_status_update(
        status="running",
        active_positions=3,
        account_balance=10547.50,
        daily_pnl=547.50
    )
    
    print("✅ Status update sent to Telegram!\n")


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "SNIPER TRADING BOT - TELEGRAM NOTIFICATIONS DEMO".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n📱 This demo will send REAL Telegram notifications to your chat!")
    print("✅ Check your Telegram to see the messages being sent.\n")
    
    input("Press ENTER to start demo...")
    
    try:
        # Run all demos
        await demo_opportunity_detection()
        await asyncio.sleep(2)
        
        await demo_trade_execution()
        await asyncio.sleep(2)
        
        await demo_trade_closed()
        await asyncio.sleep(2)
        
        await demo_daily_summary()
        await asyncio.sleep(2)
        
        await demo_error_alert()
        await asyncio.sleep(2)
        
        await demo_status_update()
        
        print("\n" + "="*80)
        print("✅ DEMO COMPLETED!")
        print("="*80)
        print("\n📱 You should have received 6 different notifications in Telegram:")
        print("   1. 🎯 Opportunity Detection Alert")
        print("   2. 🚀 Trade Execution Alert")
        print("   3. 💰 Trade Closed (Profit) Alert")
        print("   4. 📊 Daily Trading Summary")
        print("   5. ⚠️ Error and Warning Alerts")
        print("   6. 🟢 Bot Status Update\n")
        print("To run the actual bot, use: python main.py\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
