import os
import json
import random
import logging
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token
TOKEN = "7660338962:AAHxegOTNOpZSvmgedaCSKEiR-_NgW2pgS0"

# Admin username
ADMIN_USERNAME = "jarixtrader"

# Database file
DB_FILE = "users.json"

# Currency pairs
CURRENCY_PAIRS = [
    "EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF", "AUD/USD", "USD/CAD",
    "NZD/USD", "USD/PKR", "USD/INR", "USD/TRY", "USD/MXN", "AUD/CAD",
    "AUD/CHF", "AUD/JPY", "AUD/USD", "CAD/JPY", "EUR/AUD", "EUR/CAD",
    "EUR/CHF", "EUR/GBP", "EUR/JPY", "EUR/NZD", "GBP/AUD", "GBP/CHF",
    "GBP/JPY", "GBP/NZD", "GBP/USD", "NZD/CHF", "NZD/USD", "USD/CAD", "USD/CHF"
]

# Expiration times
EXPIRATION_TIMES = [
    "5 Seconds", "15 Seconds", "30 Seconds", "1 Minute", "5 Minutes"
]

# Database functions
def load_database():
    """Load user database from JSON file"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return []

def save_database(data):
    """Save user database to JSON file"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_user(user_id, database):
    """Get user from database by user_id"""
    for user in database:
        if user["user_id"] == user_id:
            return user
    return None

def add_user(user_id, username, database):
    """Add new user to database"""
    new_user = {
        "user_id": user_id,
        "username": username,
        "signals_used": 0,
        "is_premium": False
    }
    database.append(new_user)
    save_database(database)
    return new_user

def update_signals_used(user_id, database):
    """Update signals used count for a user"""
    for user in database:
        if user["user_id"] == user_id:
            user["signals_used"] += 1
            save_database(database)
            return user
    return None

# Signal generation functions
def analyze_market(currency_pair=None):
    """Perform technical analysis on market data"""
    # In a real implementation, you would fetch actual market data here
    # For now, we'll simulate technical analysis with more realistic patterns
    
    # Simulate moving averages (MA)
    short_ma = 100 + random.uniform(-5, 5)  # Short-term MA
    long_ma = 100 + random.uniform(-2, 2)   # Long-term MA
    ma_diff = short_ma - long_ma
    
    # Simulate Relative Strength Index (RSI)
    rsi = random.uniform(30, 70)  # RSI between 30-70 is neutral zone
    
    # Simulate support and resistance levels
    current_price = 100 + random.uniform(-10, 10)
    support_level = current_price - random.uniform(2, 5)
    resistance_level = current_price + random.uniform(2, 5)
    
    # Determine trend strength based on technical indicators
    if abs(ma_diff) < 1:
        trend_strength = "Weak"
    elif abs(ma_diff) < 3:
        trend_strength = "Moderate"
    else:
        trend_strength = "Strong"
    
    # Determine volatility based on price action
    price_volatility = random.uniform(0, 10)
    if price_volatility < 3:
        volatility = "Low"
    elif price_volatility < 7:
        volatility = "Stable"
    else:
        volatility = "High"
    
    # Simulate news impact (in real implementation, would fetch actual news)
    market_sentiment = random.uniform(-1, 1)
    if market_sentiment < -0.3:
        news_impact = "Negative"
    elif market_sentiment > 0.3:
        news_impact = "Positive"
    else:
        news_impact = "Neutral"
    
    # Calculate recommendation based on technical indicators
    bullish_signals = 0
    bearish_signals = 0
    
    # MA crossover signal
    if ma_diff > 0:
        bullish_signals += 1
    else:
        bearish_signals += 1
    
    # RSI signal
    if rsi < 30:  # Oversold condition
        bullish_signals += 1
    elif rsi > 70:  # Overbought condition
        bearish_signals += 1
    
    # Support/Resistance signal
    price_to_support = current_price - support_level
    price_to_resistance = resistance_level - current_price
    
    if price_to_support < price_to_resistance and price_to_support < 1:
        bullish_signals += 1  # Price near support, likely to bounce up
    elif price_to_resistance < price_to_support and price_to_resistance < 1:
        bearish_signals += 1  # Price near resistance, likely to bounce down
    
    # News impact adjustment
    if news_impact == "Positive":
        bullish_signals += 1
    elif news_impact == "Negative":
        bearish_signals += 1
    
    # Calculate accuracy based on signal strength and consistency
    signal_strength = abs(bullish_signals - bearish_signals)
    base_accuracy = 70 + (signal_strength * 5)
    accuracy = min(base_accuracy, 98)  # Cap at 98% to be realistic
    
    # Final recommendation
    recommendation = "UP" if bullish_signals > bearish_signals else "DOWN"
    
    return {
        "accuracy": int(accuracy),
        "trend_strength": trend_strength,
        "volatility": volatility,
        "news_impact": news_impact,
        "recommendation": recommendation
    }

def get_high_quality_signal():
    """Get high quality signal for trial users"""
    for _ in range(5):  # Try 5 times to get a high-quality signal
        analysis = analyze_market()
        
        if (
            analysis['accuracy'] >= 90
            and analysis['trend_strength'] == "Strong"
            and analysis['volatility'] in ["High", "Stable"]
            and analysis['news_impact'] != "Negative"
        ):
            return analysis, True
    
    return None, False

def get_live_signal():
    """Get live signal for premium users"""
    analysis = analyze_market()
    return analysis, True

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or str(user_id)
    
    # Load database
    database = load_database()
    
    # Check if user exists in database
    user = get_user(user_id, database)
    
    if not user:
        # Add new user to database
        user = add_user(user_id, f"@{username}", database)
    
    # Check trial status
    trial_status = "ACTIVE" if user["signals_used"] < 3 else "EXPIRED"
    signals_left = max(0, 3 - user["signals_used"])
    
    if user["is_premium"]:
        message = (
            f"🤖 Welcome to Jarix AI Signal Bot!\n\n"
            f"Premium Status: ✅ ACTIVE\n"
            f"Signals: Unlimited\n\n"
        )
    else:
        message = (
            f"🤖 Welcome to Jarix AI Signal Bot!\n\n"
            f"Trial Status: {trial_status} ({signals_left} signals left)\n"
            f"Premium: Contact @{jarixtrader} for upgrade.\n\n"
        )
    
    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("💹 Choose a Currency Pair", callback_data="choose_pair")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    database = load_database()
    user = get_user(user_id, database)
    
    if not user:
        username = update.effective_user.username or str(user_id)
        user = add_user(user_id, f"@{username}", database)
    
    # Check if trial is expired for non-premium users
    if not user["is_premium"] and user["signals_used"] >= 3 and not query.data.startswith("admin_"):
        await query.edit_message_text(
            text="⚠️ Trial expired. Buy Premium from @" + ADMIN_USERNAME,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
            ])
        )
        return
    
    if query.data == "choose_pair":
        # Show currency pair selection
        keyboard = []
        row = []
        
        for i, pair in enumerate(CURRENCY_PAIRS):
            row.append(InlineKeyboardButton(pair, callback_data=f"pair_{pair}"))
            
            if (i + 1) % 3 == 0 or i == len(CURRENCY_PAIRS) - 1:
                keyboard.append(row)
                row = []
        
        await query.edit_message_text(
            text="Select a currency pair:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data.startswith("pair_"):
        # Store selected pair in user_data
        selected_pair = query.data.replace("pair_", "")
        context.user_data["selected_pair"] = selected_pair
        
        # Show expiration time selection
        keyboard = []
        for time in EXPIRATION_TIMES:
            keyboard.append([InlineKeyboardButton(f"🕐 {time}", callback_data=f"time_{time}")])
        
        await query.edit_message_text(
            text=f"Selected pair: {selected_pair}\nNow select expiration time:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif query.data.startswith("time_"):
        # Store selected time in user_data
        selected_time = query.data.replace("time_", "")
        selected_pair = context.user_data.get("selected_pair", "Unknown")
        
        # Generate signal based on user type
        if user["is_premium"]:
            analysis, signal_available = get_live_signal()
        else:
            analysis, signal_available = get_high_quality_signal()
            if signal_available:
                update_signals_used(user_id, database)
        
        if signal_available:
            # Format signal message
            signal_message = (
                f"📢 Jarix AI Signal:\n\n"
                f"💹 Pair: {selected_pair}\n"
                f"🕐 Time: {selected_time}\n"
                f"📰 News: {analysis['news_impact']}\n"
                f"📊 Volatility: {analysis['volatility']}\n"
                f"📈 Trend: {'Uptrend' if analysis['recommendation'] == 'UP' else 'Downtrend'}\n\n"
                f"Recommendation: {'⬆ UP' if analysis['recommendation'] == 'UP' else '⬇ DOWN'}"
            )=
            
            # Add back button
            keyboard = [
                [InlineKeyboardButton("🔄 Get Another Signal", callback_data="choose_pair")]
            ]
            
            await query.edit_message_text(
                text=signal_message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                text="⚠️ No strong signal now. Please wait or try another pair!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="choose_pair")]
                ])
            )

# Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Jarix Bot Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# Main function
def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the keep-alive server
    keep_alive()
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()