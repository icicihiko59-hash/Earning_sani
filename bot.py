import logging
import sqlite3
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import os

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Bot Token
TOKEN = '8767484201:AAE00ymNQjlJWHlgXIRHnPe8f0gmf0-UsYc'

# Database setup
def setup_database():
    conn = sqlite3.connect('earning_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, user_id INTEGER UNIQUE, name TEXT, balance REAL, clicks INTEGER, created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = sqlite3.connect('earning_bot.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM users WHERE user_id=?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def add_balance(user_id, amount):
    conn = sqlite3.connect('earning_bot.db')
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE user_id=?', (amount, user_id))
    conn.commit()
    conn.close()

def register_user(user_id, name):
    conn = sqlite3.connect('earning_bot.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (user_id, name, balance, clicks) VALUES (?, ?, 0, 0)', (user_id, name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# Commands
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name
    register_user(user_id, name)
    
    keyboard = [
        [InlineKeyboardButton("💰 আয় করুন", callback_data='earn')],
        [InlineKeyboardButton("💵 ব্যালেন্স", callback_data='balance')],
        [InlineKeyboardButton("👥 রেফার করুন", callback_data='refer')],
        [InlineKeyboardButton("❓ সাহায্য", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'স্বাগতম {name}! 🎉\n\nটেলিগ্রাম আর্নিং বটে আপনাকে স্বাগতম! এখানে আপনি ক্লিক করে টাকা আয় করতে পারেন।', reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
    🤖 **বট সাহায্য:**
    
    /start - বট শুরু করুন
    /help - এই সাহায্য পান
    /balance - আপনার ব্যালেন্স দেখুন
    /earn - আয় করুন
    /refer - রেফারেল লিংক পান
    
    💡 **কীভাবে আয় করবেন:**
    1. প্রতিদিন ক্লিক করে পয়েন্ট আর্ন করুন
    2. বন্ধুদের রেফার করুন এবং বোনাস পান
    3. আপনার ব্যালেন্স চেক করুন
    """
    update.message.reply_text(help_text, parse_mode='Markdown')

def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == 'earn':
        add_balance(user_id, 10)
        query.answer()
        query.edit_message_text(text="✅ আপনি ১০ টাকা আয় করেছেন!")
    elif query.data == 'balance':
        balance = get_user_balance(user_id)
        query.answer()
        query.edit_message_text(text=f"💵 আপনার ব্যালেন্স: {balance} টাকা")
    elif query.data == 'refer':
        query.answer()
        query.edit_message_text(text=f"👥 আপনার রেফারেল লিংক:\nhttps://t.me/earning_sani_bot?start={user_id}")
    elif query.data == 'help':
        help_text = """
        🤖 **বট সাহায্য:**
        
        💡 **কীভাবে আয় করবেন:**
        1. প্রতিদিন ক্লিক করে পয়েন্ট আর্ন করুন (১০ টাকা প্রতিটি ক্লিক)
        2. বন্ধুদের রেফার করুন এবং বোনাস পান (৫০ টাকা প্রতি রেফারেল)
        3. আপনার ব্যালেন্স চেক করুন
        """
        query.answer()
        query.edit_message_text(text=help_text, parse_mode='Markdown')

def main() -> None:
    setup_database()
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Register handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CallbackQueryHandler(button_callback))
    
    # Run the bot
    updater.start_polling()
    logger.info("Bot started successfully!")
    updater.idle()

if __name__ == '__main__':
    main()
