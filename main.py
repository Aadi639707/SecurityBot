import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from flask import Flask
from threading import Thread

# --- RENDER SERVER ---
webapp = Flask(__name__)
@webapp.route('/')
def index(): return "Security Bot is Live!"
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    webapp.run(host='0.0.0.0', port=port)

# --- BOT CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Yahan humne prefixes badal diye hain taaki bot responsive rahe
app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary Settings
group_settings = {"abuse": True, "welcome": True}
authorized_users = []

# Admin Check Helper
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except: return False

# --- COMMANDS WITH USERNAME SUPPORT ---

# 1. Start Command
@app.on_message(filters.command(["start", f"start@{(BOT_TOKEN.split(':')[0])}"]))
async def start_handler(client, message):
    bot = await client.get_me()
    text = (
        f"🔐 Hello {message.from_user.mention}, welcome to Security Bot!\n\n"
        "✨ **Your Personal Chat Bodyguard is active!**\n\n"
        "Use buttons below to explore:"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), 
         InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")],
        [InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot.username}?startgroup=true")],
        [InlineKeyboardButton("📜 Help & Commands", callback_data="help_menu"),
         InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SANATANI_GOJO")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# 2. Abuse Command Fix (Ab ye pakka chalega)
@app.on_message(filters.command(["abuse", "abuse@GcSecurityProbot"]) & filters.group)
async def abuse_toggle(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
    
    if len(message.command) > 1:
        choice = message.command[1].lower()
        if choice in ["enable", "on"]:
            group_settings["abuse"] = True
            await message.reply("🚫 **Anti-Abuse filter is now ENABLED.**")
        elif choice in ["disable", "off"]:
            group_settings["abuse"] = False
            await message.reply("✅ **Anti-Abuse filter is now DISABLED.**")
    else:
        await message.reply("Usage: `/abuse enable` or `/abuse disable`")

# 3. Settings Command
@app.on_message(filters.command(["settings", "settings@GcSecurityProbot"]) & filters.group)
async def settings_handler(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    await message.reply("⚙️ **Settings Menu Open** (Check Private or Inline)")

# 4. Auth/Unauth (Reply base)
@app.on_message(filters.command(["auth", "unauth"]) & filters.group)
async def auth_logic(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message:
        return await message.reply("Reply to a user to Auth/Unauth.")
    
    uid = message.reply_to_message.from_user.id
    if message.command[0] == "auth":
        if uid not in authorized_users: authorized_users.append(uid)
        await message.reply(f"✅ User {uid} Authorized.")
    else:
        if uid in authorized_users: authorized_users.remove(uid)
        await message.reply(f"❌ User {uid} Unauthorized.")

# --- AUTO DELETE MEDIA ---
@app.on_message(filters.group & ~filters.service)
async def auto_delete(client, message):
    if await is_admin(message.chat.id, message.from_user.id) or message.from_user.id in authorized_users:
        return
    if message.media or message.edit_date:
        await message.delete()

# --- RUN ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    app.run()
    
