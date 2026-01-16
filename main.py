import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from flask import Flask
from threading import Thread

# --- RENDER ALIVE SERVER ---
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

# 'prefixes' add karne se bot / aur ! dono se commands uthayega
app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary Database
group_settings = {"welcome": True, "captcha": True, "abuse": True}
authorized_users = []

# Admin Check Helper
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except: return False

# --- COMMANDS LOGIC ---

# 1. Start Command (Works everywhere)
@app.on_message(filters.command("start") & (filters.private | filters.group))
async def start_handler(client, message):
    bot = await client.get_me()
    text = (
        f"🔐 Hello {message.from_user.mention}, welcome to Security Bot!\n\n"
        "✨ **Your Personal Chat Bodyguard is active!**\n\n"
        "Use the buttons below to explore features:"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), 
         InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")],
        [InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot.username}?startgroup=true")],
        [InlineKeyboardButton("📜 Help & Commands", callback_data="help_menu"),
         InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SANATANI_GOJO")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# 2. Settings Command (/settings)
@app.on_message(filters.command("settings") & filters.group)
async def settings_handler(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Only Admins can use this command.")
    
    status_w = "✅ ON" if group_settings["welcome"] else "❌ OFF"
    status_c = "✅ ON" if group_settings["captcha"] else "❌ OFF"
    text = f"⚙️ **Control Panel**\n\nWelcome: {status_w}\nCaptcha: {status_c}"
    buttons = [[InlineKeyboardButton("Toggle Welcome", callback_data="toggle_w")],
               [InlineKeyboardButton("Toggle Captcha", callback_data="toggle_c")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# 3. Abuse Toggle (/abuse enable or /abuse disable)
@app.on_message(filters.command("abuse") & filters.group)
async def abuse_handler(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    
    if len(message.command) > 1:
        choice = message.command[1].lower()
        if choice in ["enable", "on"]:
            group_settings["abuse"] = True
            await message.reply("🚫 Anti-Abuse filter is now **ENABLED**.")
        elif choice in ["disable", "off"]:
            group_settings["abuse"] = False
            await message.reply("✅ Anti-Abuse filter is now **DISABLED**.")
    else:
        await message.reply("Usage: `/abuse enable` or `/abuse disable`.")

# 4. Auth & Unauth Logic
@app.on_message(filters.command(["auth", "unauth"]) & filters.group)
async def auth_logic(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message:
        return await message.reply("Reply to a user's message to authorize them.")
    
    user_id = message.reply_to_message.from_user.id
    cmd = message.command[0].lower()
    
    if cmd == "auth":
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            await message.reply(f"✅ User `{user_id}` has been authorized.")
    else:
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            await message.reply(f"❌ User `{user_id}` authorization removed.")

# --- CALLBACKS ---
@app.on_callback_query()
async def callbacks(client, cb):
    if cb.data == "help_menu":
        text = "📖 **Help Menu**\n\n/start - Open Menu\n/settings - Toggle Panels\n/auth - Whitelist user\n/abuse - Filter bad words"
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_home")]]))
    elif cb.data == "back_home":
        await cb.message.delete()
        await start_handler(client, cb.message)

# --- AUTOMATIC PROTECTION ---
@app.on_message(filters.group & ~filters.service)
async def protect(client, message):
    # Admins aur Authorized users ko skip karein
    if await is_admin(message.chat.id, message.from_user.id) or message.from_user.id in authorized_users:
        return
    
    # Delete Media
    if message.media:
        await message.delete()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    app.run()
    
