import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- WEB SERVER ---
webapp = Flask(__name__)
@webapp.route('/')
def index(): return "Security Bot is Live!"
def run_flask():
    webapp.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- BOT CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Force response for group commands
app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command(["start", "help"]) & (filters.private | filters.group))
async def start_handler(client, message):
    bot = await client.get_me()
    text = "🔐 **Security Bot Main Menu**\n\nChoose an option below:"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), 
         InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")],
        [InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot.username}?startgroup=true")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SANATANI_GOJO")]
    ])
    await message.reply_text(text, reply_markup=buttons)

@app.on_message(filters.command(["settings", "abuse", "auth"]) & filters.group)
async def group_commands(client, message):
    # Testing if bot is even reading group messages
    await message.reply_text(f"✅ Command Received: {message.text}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    app.run()
    
