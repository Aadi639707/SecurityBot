import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from flask import Flask
from threading import Thread

# 1. WEB SERVER FOR RENDER
webapp = Flask(__name__)

@webapp.route('/')
def index():
    return "Security Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    webapp.run(host='0.0.0.0', port=port)

# 2. BOT CONFIGURATION
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Default Settings
group_settings = {
    "welcome_enabled": True,
    "captcha_enabled": True
}

# 3. ADMIN CHECK HELPER
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

# 4. PROFESSIONAL START MENU
@app.on_message(filters.command("start"))
async def start(client, message):
    bot = await client.get_me()
    text = (
        "🔐 **Hello! Welcome to Security Bot!**\n\n"
        "✨ **Your Personal Chat Bodyguard is here!**\n\n"
        "🚀 **Features:**\n"
        "• Instantly deletes **edited messages**.\n"
        "• Auto-removes all types of **media**.\n"
        "• Cleans abusive words and spam.\n"
        "• Flexible **admin controls** & captcha.\n\n"
        "💡 *Keep your chat clean, safe, and spam-free!*"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), 
            InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")
        ],
        [
            InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot.username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📜 Help & Commands", callback_data="help_menu"),
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SANATANI_GOJO")
        ]
    ])
    await message.reply_text(text, reply_markup=buttons)

# 5. HELP MENU
@app.on_callback_query(filters.regex("help_menu"))
async def help_menu(client, cb):
    help_text = (
        "📖 **Security Bot Commands:**\n\n"
        "• `/start` — Open main menu\n"
        "• `/settings` — Toggle Welcome/Captcha\n"
        "• `/auth` — Authorize a user (Coming Soon)\n"
        "• `/unauth` — Remove authorization\n\n"
        "🛡️ *Admin rights are required for the bot to function.*"
    )
    await cb.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_home")]
    ]))

@app.on_callback_query(filters.regex("back_home"))
async def back_home(client, cb):
    bot = await client.get_me()
    text = "🔐 **Security Bot Main Menu**\n\nChoose an option below:"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")],
        [InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot.username}?startgroup=true")],
        [InlineKeyboardButton("📜 Help & Commands", callback_data="help_menu"), InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SANATANI_GOJO")]
    ])
    await cb.message.edit_text(text, reply_markup=buttons)

# 6. SECURITY LOGIC
@app.on_edited_message(filters.group)
async def del_edit(client, message):
    await message.delete()

@app.on_message(filters.media & filters.group)
async def del_media(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.delete()

# 7. WELCOME & CAPTCHA VERIFICATION
@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for m in message.new_chat_members:
        if group_settings["captcha_enabled"]:
            await client.restrict_chat_member(message.chat.id, m.id, ChatPermissions(can_send_messages=False))
            await message.reply_text(
                f"Welcome {m.mention}! Please verify yourself to join the conversation.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Click to Verify", callback_data=f"verify_{m.id}")
                ]])
            )
        elif group_settings["welcome_enabled"]:
            await message.reply_text(f"Welcome {m.mention} to the group!")

@app.on_callback_query(filters.regex("^verify_"))
async def verify_user(client, cb):
    user_id = int(cb.data.split("_")[1])
    if cb.from_user.id != user_id:
        return await cb.answer("❌ This button is for the new member only!", show_alert=True)
    
    await client.unban_chat_member(cb.message.chat.id, user_id)
    await cb.message.edit_text(f"✅ {cb.from_user.mention} has been verified and unmuted!")

# 8. STARTUP
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    app.run()
    
