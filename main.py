import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from flask import Flask
from threading import Thread

# --- WEB SERVER FOR RENDER ---
webapp = Flask(__name__)
@webapp.route('/')
def index(): return "Security Bot is running!"
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    webapp.run(host='0.0.0.0', port=port)

# --- BOT CONFIGURATION ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary Database (Restart par reset hoga - Database ke bina yahi option hai)
group_settings = {
    "welcome_enabled": True,
    "captcha_enabled": True,
    "anti_abuse": True,
    "media_delay": 0  # 0 means instant delete
}
authorized_users = [] # Whitelisted users list

# --- HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except: return False

# --- COMMANDS LOGIC ---

# 1. Start & Help (UI Setup)
@app.on_message(filters.command("start"))
async def start(client, message):
    bot = await client.get_me()
    text = (
        "🔐 **Security Bot Main Menu**\n\n"
        "✨ Your Personal Chat Bodyguard is active!\n\n"
        "Use buttons below to navigate:"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), 
         InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")],
        [InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot.username}?startgroup=true")],
        [InlineKeyboardButton("📜 Help & Commands", callback_data="help_menu"),
         InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SANATANI_GOJO")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# 2. Settings Command
@app.on_message(filters.command("settings") & filters.group)
async def settings_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    status_w = "✅ ON" if group_settings["welcome_enabled"] else "❌ OFF"
    status_c = "✅ ON" if group_settings["captcha_enabled"] else "❌ OFF"
    text = f"⚙️ **Control Panel**\n\nWelcome: {status_w}\nCaptcha: {status_c}"
    buttons = [[InlineKeyboardButton("Toggle Welcome", callback_data="toggle_welcome")],
               [InlineKeyboardButton("Toggle Captcha", callback_data="toggle_captcha")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# 3. Auth Command (Authorize User)
@app.on_message(filters.command("auth") & filters.group)
async def auth_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            await message.reply_text(f"✅ User {user_id} has been authorized!")
        else:
            await message.reply_text("This user is already authorized.")
    else:
        await message.reply_text("Reply to a user's message to authorize them.")

# 4. Unauth Command
@app.on_message(filters.command("unauth") & filters.group)
async def unauth_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            await message.reply_text(f"❌ User {user_id} authorization removed.")
    else:
        await message.reply_text("Reply to a user to unauthorize.")

# 5. Abuse Filter Toggle
@app.on_message(filters.command("abuse") & filters.group)
async def toggle_abuse(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    group_settings["anti_abuse"] = not group_settings["anti_abuse"]
    status = "Enabled" if group_settings["anti_abuse"] else "Disabled"
    await message.reply_text(f"🚫 Anti-Abuse filter is now **{status}**.")

# --- CALLBACKS ---
@app.on_callback_query()
async def cb_handler(client, cb):
    if cb.data == "help_menu":
        help_text = (
            "📖 **Security Bot Commands:**\n\n"
            "• `/start` — Main Menu\n"
            "• `/settings` — Toggle Welcome/Captcha\n"
            "• `/auth` — Whitelist a user (Reply to msg)\n"
            "• `/unauth` — Remove from whitelist\n"
            "• `/abuse` — Toggle Bad Word Filter\n"
            "• `/delay` — Set media deletion delay\n"
        )
        await cb.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_home")]
        ]))
    elif cb.data == "back_home":
        await start(client, cb.message)
        await cb.message.delete()
    # Settings toggles (logic already in previous versions)
    elif cb.data == "toggle_welcome":
        group_settings["welcome_enabled"] = not group_settings["welcome_enabled"]
        await cb.answer("Welcome Toggled")
    elif cb.data == "toggle_captcha":
        group_settings["captcha_enabled"] = not group_settings["captcha_enabled"]
        await cb.answer("Captcha Toggled")

# --- AUTO PROTECTION ---
@app.on_message(filters.group & ~filters.service)
async def protection_logic(client, message):
    if await is_admin(message.chat.id, message.from_user.id) or message.from_user.id in authorized_users:
        return

    # Anti-Media
    if message.media:
        await message.delete()

# --- RUN ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    app.run()
    
