import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from flask import Flask
from threading import Thread

# --- RENDER ALIVE SERVER ---
webapp = Flask(__name__)

@webapp.route('/')
def index():
    return "Security Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    webapp.run(host='0.0.0.0', port=port)

# --- BOT CONFIGURATION ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Default Settings
group_settings = {
    "welcome_enabled": True,
    "captcha_enabled": True
}

# --- ADMIN CHECK HELPER ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

# --- MAIN MENU (START) ---
@app.on_message(filters.command("start"))
async def start(client, message):
    bot = await client.get_me()
    text = (
        "🔐 **Hello! Welcome to Security Bot!**\n\n"
        "✨ **Your Personal Chat Bodyguard is here!**\n\n"
        "🚀 **Features:**\n"
        "• Instantly deletes **edited messages** to prevent confusion.\n"
        "• Auto-removes all types of **media** – photos, videos, stickers.\n"
        "• Cleans abusive words to keep your group respectful.\n"
        "• Offers flexible **admin controls** like captcha and toggles.\n\n"
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

# --- SETTINGS PANEL ---
@app.on_message(filters.command("settings") & filters.group)
async def settings_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ **Admins only.**")
    
    status_w = "✅ ON" if group_settings["welcome_enabled"] else "❌ OFF"
    status_c = "✅ ON" if group_settings["captcha_enabled"] else "❌ OFF"
    
    text = f"⚙️ **Control Panel**\n\nWelcome: {status_w}\nCaptcha: {status_c}"
    buttons = [[InlineKeyboardButton("Toggle Welcome", callback_data="toggle_welcome")],
               [InlineKeyboardButton("Toggle Captcha", callback_data="toggle_captcha")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- CALLBACK HANDLERS ---
@app.on_callback_query()
async def cb_handler(client, cb):
    if not await is_admin(cb.message.chat.id, cb.from_user.id):
        return await cb.answer("You are not an Admin!", show_alert=True)
    
    if cb.data == "help_menu":
        help_text = (
            "📖 **Available Commands:**\n\n"
            "🔹 `/start` — Show main menu\n"
            "🔹 `/settings` — Admin toggle panel\n"
            "🔹 `/help` — View this command list\n"
            "🔹 `/auth` — Authorize a user\n"
            "🔹 `/unauth` — Remove authorization\n"
            "🔹 `/authlist` — View authorized users\n"
            "🔹 `/delay` — Set deletion delay\n"
            "🔹 `/abuse` — Abusive word filter\n\n"
            "Click back to return to the main menu."
        )
        return await cb.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_home")]
        ]))

    if cb.data == "back_home":
        bot = await client.get_me()
        text = "🔐 **Security Bot Main Menu**\n\nChoose an option below:"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")],
            [InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot.username}?startgroup=true")],
            [InlineKeyboardButton("📜 Help & Commands", callback_data="help_menu"), InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SANATANI_GOJO")]
        ])
        return await cb.message.edit_text(text, reply_markup=buttons)

    if cb.data == "toggle_welcome":
        group_settings["welcome_enabled"] = not group_settings["welcome_enabled"]
    elif cb.data == "toggle_captcha":
        group_settings["captcha_enabled"] = not group_settings["captcha_enabled"]
    elif cb.data.startswith("verify_"):
        user_id = int(cb.data.split("_")[1])
        if cb.from_user.id != user_id:
            return await cb.answer("❌ Not for you!", show_alert=True)
        await client.unban_chat_member(cb.message.chat.id, user_id)
        return await cb.message.edit_text(f"✅ {cb.from_user.mention} verified successfully!")

    # Refresh Settings View
    status_w = "✅ ON" if group_settings["welcome_enabled"] else "❌ OFF"
    status_c = "✅ ON" if group_settings["captcha_enabled"] else "❌ OFF"
    await cb.message.edit_text(f"⚙️ **Control Panel**\n\nWelcome: {status_w}\nCaptcha: {status_c}",
                               reply_markup=cb.message.reply_markup)

# --- SECURITY LOGIC ---
@app.on_edited_message(filters.group)
async def del_edit(client, message):
    await message.delete()

@app.on_message(filters.media & filters.group)
async def del_media(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.delete()

@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for m in message.new_chat_members:
        if group_settings["captcha_enabled"]:
            await client.restrict_chat_member(message.chat.id, m.id, ChatPermissions(can_send_messages=False))
            await message.reply_text(f"Welcome {m.mention}! Please verify yourself.",
                                     reply_markup=InlineKeyboardMarkup([[
                                         InlineKeyboardButton("✅ Verify Me", callback_data=f"verify_{m.id}")
                                     ]]))
        elif group_settings["welcome_enabled"]:
            await message.reply_text(f"Welcome {m.mention} to the group!")

# --- EXECUTION ---
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    app.run()
    
