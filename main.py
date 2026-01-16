import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from flask import Flask
from threading import Thread

# --- WEB SERVER CONFIG ---
webapp = Flask(__name__)

@webapp.route('/')
def index():
    return "Security Bot is running!"

def run_flask():
    # Render provides the PORT variable automatically
    port = int(os.environ.get("PORT", 8080))
    webapp.run(host='0.0.0.0', port=port)

# --- BOT CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Settings
group_settings = {
    "welcome_enabled": True,
    "captcha_enabled": True
}

async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🛡️ **Security Bot Active**\n\nI protect your group from spam and unauthorized media.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Settings", callback_data="open_settings")
        ]])
    )

@app.on_message(filters.command("settings") & filters.group)
async def settings_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Admins only.")
    
    status_w = "✅ ON" if group_settings["welcome_enabled"] else "❌ OFF"
    status_c = "✅ ON" if group_settings["captcha_enabled"] else "❌ OFF"
    
    text = f"⚙️ **Control Panel**\n\nWelcome: {status_w}\nCaptcha: {status_c}"
    buttons = [[InlineKeyboardButton("Toggle Welcome", callback_data="toggle_welcome")],
               [InlineKeyboardButton("Toggle Captcha", callback_data="toggle_captcha")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
async def cb_handler(client, cb):
    if not await is_admin(cb.message.chat.id, cb.from_user.id):
        return await cb.answer("Admin only!", show_alert=True)
    if cb.data == "toggle_welcome":
        group_settings["welcome_enabled"] = not group_settings["welcome_enabled"]
    elif cb.data == "toggle_captcha":
        group_settings["captcha_enabled"] = not group_settings["captcha_enabled"]
    
    status_w = "✅ ON" if group_settings["welcome_enabled"] else "❌ OFF"
    status_c = "✅ ON" if group_settings["captcha_enabled"] else "❌ OFF"
    await cb.message.edit_text(f"⚙️ **Control Panel**\n\nWelcome: {status_w}\nCaptcha: {status_c}",
                               reply_markup=cb.message.reply_markup)

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
            await message.reply_text(f"Welcome {m.mention}! Tap the button below to verify.",
                                     reply_markup=InlineKeyboardMarkup([[
                                         InlineKeyboardButton("Verify Me", callback_data=f"verify_{m.id}")
                                     ]]))
        elif group_settings["welcome_enabled"]:
            await message.reply_text(f"Welcome {m.mention}!")

@app.on_callback_query(filters.regex("^verify_"))
async def verify_user(client, cb):
    user_id = int(cb.data.split("_")[1])
    if cb.from_user.id != user_id:
        return await cb.answer("This is not for you!", show_alert=True)
    
    await client.unban_chat_member(cb.message.chat.id, user_id) # This restores permissions
    await cb.message.edit_text(f"✅ {cb.from_user.mention} verified successfully!")

# --- EXECUTION ---
if __name__ == "__main__":
    # Start Flask in a background thread
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Start the Bot
    print("Bot starting...")
    app.run()
    
