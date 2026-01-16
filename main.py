@app.on_message(filters.command("start"))
async def start(client, message):
    # Fetch bot username automatically for the 'Add Me' link
    bot_username = (await client.get_me()).username
    
    # Professional English Text
    text = (
        "🔐 **Hello! Welcome to Security Bot!**\n\n"
        "✨ **Your Personal Chat Bodyguard is here!**\n\n"
        "🚀 **Features:**\n"
        "• Instantly deletes **edited messages** to prevent confusion.\n"
        "• Auto-removes all types of **media** – photos, videos, etc.\n"
        "• Cleans abusive words to keep your group respectful.\n"
        "• Offers flexible **admin controls** like captcha and toggles.\n\n"
        "💡 *Keep your chat clean, safe, and spam-free!*"
    )

    # Professional Buttons Layout (Same as the screenshot)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Updates 📢", url="https://t.me/SANATANI_METHODS"), # Replace with your link
            InlineKeyboardButton("Support 💬", url="https://t.me/chattinggcand")    # Replace with your link
        ],
        [
            InlineKeyboardButton("➕ Add to Secure Your Chat", url=f"https://t.me/{bot_username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📜 Help & Commands", callback_data="help_menu")
        ]
    ])

    await message.reply_text(text, reply_markup=buttons)

# Callback for Help Menu
@app.on_callback_query(filters.regex("help_menu"))
async def help_callback(client, cb):
    help_text = (
        "📖 **Available Commands:**\n\n"
        "• `/start` — Show main menu\n"
        "• `/settings` — Configure bot toggles\n"
        "• `/auth` — Exempt a user (Coming Soon)\n"
        "• `/delay` — Set deletion time (Coming Soon)\n\n"
        "📝 *Note: Default media deletion is instant for non-admins.*"
    )
    await cb.message.edit_text(
        help_text, 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_start")]])
    )

@app.on_callback_query(filters.regex("back_to_start"))
async def back_home(client, cb):
    # This will trigger the start function again to show the main menu
    await start(client, cb.message)
    await cb.message.delete()
    
