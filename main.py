import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# API Credentials
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("SecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary Settings (Bot restart hone par reset ho jayengi, permanent ke liye Database chahiye)
settings = {
    "welcome_enabled": True,
    "captcha_enabled": True
}

# --- COMMANDS ---

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🛡️ **Security Bot Active!**\n\nMain aapke group ko safe rakhunga.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Help & Commands", callback_data="help")]
        ])
    )

@app.on_message(filters.command("settings") & filters.group)
async def settings_panel(client, message):
    # Check if user is admin
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in ["administrator", "creator"]:
        return await message.reply("Sirf Admins hi settings badal sakte hain!")

    text = f"**Bot Settings Control:**\n\nWelcome Image: {'✅ ON' if settings['welcome_enabled'] else '❌ OFF'}\nCaptcha: {'✅ ON' if settings['captcha_enabled'] else '❌ OFF'}"
    
    buttons = [
        [InlineKeyboardButton("Toggle Welcome", callback_data="toggle_welcome")],
        [InlineKeyboardButton("Toggle Captcha", callback_data="toggle_captcha")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- HANDLERS ---

@app.on_callback_query()
async def handle_buttons(client, cb):
    if cb.data == "toggle_welcome":
        settings["welcome_enabled"] = not settings["welcome_enabled"]
    elif cb.data == "toggle_captcha":
        settings["captcha_enabled"] = not settings["captcha_enabled"]
    
    # Update the message
    text = f"**Bot Settings Control:**\n\nWelcome Image: {'✅ ON' if settings['welcome_enabled'] else '❌ OFF'}\nCaptcha: {'✅ ON' if settings['captcha_enabled'] else '❌ OFF'}"
    await cb.message.edit_text(text, reply_markup=cb.message.reply_markup)

# New Member Handler
@app.on_message(filters.new_chat_members)
async def welcome_new_member(client, message):
    if settings["welcome_enabled"]:
        # Welcome Image bhejne ka logic yahan aayega
        await message.reply_text(f"Welcome {message.from_user.mention}!")
    
    if settings["captcha_enabled"]:
        # Captcha dikhane ka logic yahan aayega
        await message.reply_text("Verify karein ki aap robot nahi hain!")

app.run()
