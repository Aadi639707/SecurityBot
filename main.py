import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from threading import Thread
from flask import Flask

# --- WEB SERVER FOR RENDER (KEEPS BOT ALIVE) ---
server = Flask(__name__)
@server.route('/')
def home(): return "Security Bot is Online!"

def run_server():
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

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
    except Exception:
        return False

# --- COMMANDS ---

@app.on_message(filters.command("start") & filters.private)
async def start_private(client, message):
    await message.reply_text(
        "👋 **Welcome to Security Bot!**\n\nI am your advanced chat bodyguard. Add me to your group and make me admin to start protecting your chat.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Add Me To Your Chat", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")
        ]])
    )

@app.on_message(filters.command("settings") & filters.group)
async def settings_menu(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ **Access Denied:** Only Admins can use this command.")
    
    status_w = "✅ Enabled" if group_settings["welcome_enabled"] else "❌ Disabled"
    status_c = "✅ Enabled" if group_settings["captcha_enabled"] else "❌ Disabled"
    
    text = f"⚙️ **Bot Control Panel**\n\n**Welcome Message:** {status_w}\n**Captcha Verification:** {status_c}"
    buttons = [
        [InlineKeyboardButton("Toggle Welcome", callback_data="toggle_welcome")],
        [InlineKeyboardButton("Toggle Captcha", callback_data="toggle_captcha")],
        [InlineKeyboardButton("Close Menu", callback_data="close_menu")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- BUTTON HANDLERS ---

@app.on_callback_query()
async def handle_callbacks(client, cb):
    if not await is_admin(cb.message.chat.id, cb.from_user.id):
        return await cb.answer("You are not authorized to perform this action.", show_alert=True)

    if cb.data == "toggle_welcome":
        group_settings["welcome_enabled"] = not group_settings["welcome_enabled"]
    elif cb.data == "toggle_captcha":
        group_settings["captcha_enabled"] = not group_settings["captcha_enabled"]
    elif cb.data == "close_menu":
        return await cb.message.delete()

    # Update UI
    status_w = "✅ Enabled" if group_settings["welcome_enabled"] else "❌ Disabled"
    status_c = "✅ Enabled" if group_settings["captcha_enabled"] else "❌ Disabled"
    text = f"⚙️ **Bot Control Panel**\n\n**Welcome Message:** {status_w}\n**Captcha Verification:** {status_c}"
    
    await cb.message.edit_text(text, reply_markup=cb.message.reply_markup)

# --- SECURITY HANDLERS ---

# Anti-Edit Feature
@app.on_edited_message(filters.group)
async def anti_edit(client, message):
    await message.delete()

# Anti-Media Feature (Restricts non-admins)
@app.on_message(filters.media & filters.group)
async def anti_media(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.delete()

# New Member (Welcome & Captcha)
@app.on_message(filters.new_chat_members)
async def newcomer_logic(client, message):
    for member in message.new_chat_members:
        if group_settings["captcha_enabled"]:
            # Mute the user until they pass captcha (Logic can be expanded)
            await client.restrict_chat_member(message.chat.id, member.id, ChatPermissions(can_send_messages=False))
            await message.reply_text(f"Welcome {member.mention}! Please verify you are human.")
        
        elif group_settings["welcome_enabled"]:
            await message.reply_text(f"Welcome to the group, {member.mention}!")

# --- START BOT ---
if __name__ == "__main__":
    Thread(target=run_server).start()
    print("Security Bot is starting in English mode...")
    app.run()
    
