from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database.user import update_verification, add_user, update_membership

# inline of Start command 
def get_inline_buttons():
    keyboard = [
        [InlineKeyboardButton("🔗 Backup channel", url="https://t.me/flickwiz")],
        [InlineKeyboardButton("🔗 Share Bot", url="https://t.me/share/url?url=https://t.me/FlickWiz_bot&text=Check%20out%20this%20awesome%20movie%20bot!")]
    ]
    return InlineKeyboardMarkup(keyboard)
    
# 🎬 /start Command    
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user.id, user.username)
    full_name = user.username

    # Check if user is returning from verification
    args = context.args  # Get start parameters
    if args and args[0].startswith("verify_"):
        update_verification(user.id)  # Update verification timestamp
        await update.message.reply_text("✅ Verification successful! You can now search for movies.")
        return

    welcome_message = f"""
𝖧𝖾𝗅𝗅𝗈 👋🏻 {full_name}  

🎬 𝖶ᴇʟ𝖼𝗈𝗆𝖾 𝗍𝗈 𝗍𝗁𝖾 𝗎𝗅𝗍𝗂𝗆𝖺𝗍𝖾 𝗆𝖔𝗏𝗂𝖾 𝗁𝖚𝖻! 🍿✨ 

𝖩𝗎𝗌𝗍 𝗌𝖾𝗇𝖽 𝗆𝖾 𝖺𝗇𝗒 𝖬𝗈𝗏𝗂𝖾 𝗈𝗋 𝖲𝖾𝗋𝗂𝖾𝗌 𝗇𝖺𝗆𝖾 𝗐𝗂𝗍𝗁 𝗉𝗋𝗈𝗉𝖾𝗋 [𝖦𝗈𝗈𝗀𝗅𝖾](https://www.google.com) 𝗌𝗉𝖾𝗅𝗅𝗂𝗇𝗀, 𝖺𝗇𝖽 𝗐𝖺𝗍𝖼𝗁 𝗍𝗁𝖾 𝗆𝖺𝗀𝗂𝖼 𝗁𝖺𝗉𝗉𝖾𝗇! 🎭🔍 
"""

    # Send the welcome image with caption
    with open("welcome.jpg", "rb") as photo:
        await update.message.reply_photo(photo, caption=welcome_message, reply_markup=get_inline_buttons(), parse_mode="Markdown")


# 🔹 /help Command & Button Handler
async def help(update: Update, context: CallbackContext):
    help_message = """
🔹 *How to Use the Bot?* 🔹

📌 *Search for a Movie or Series:*  
Just send me the name of any movie or series with correct [Google](https://www.google.com) spelling, and I'll try to find it for you! 🎬  

*Example:* The Kashmir Files 
*Example:* Mismatched S01 E01

Enjoy your movies! 🍿✨
"""

    if update.callback_query:  # If triggered by a button
        query = update.callback_query
        await query.answer()

        # Check if it's a text message, else send a new message
        if query.message.text:
            await query.message.edit_text(help_message, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await query.message.reply_text(help_message, parse_mode="Markdown", disable_web_page_preview=True)
    else:  # If triggered by /help command
        await update.message.reply_text(help_message, parse_mode="Markdown", disable_web_page_preview=True)

# 🔹 /about Command & Button Handler
async def about(update: Update, context: CallbackContext):
    about_message = """
👋 Welcome to *FlickWiz Bot*!  

🎥 This bot helps you find movies and series easily.  
💡 Just type a movie name, and I'll fetch it for you!  

🚀 Powered by Python & Telegram Bot API.  

🔗 Share with friends and enjoy watching! 🍿✨
"""

    if update.callback_query:  # If triggered by a button
        query = update.callback_query
        await query.answer()

        # Check if it's a text message, else send a new message
        if query.message.text:
            await query.message.edit_text(about_message, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await query.message.reply_text(about_message, parse_mode="Markdown", disable_web_page_preview=True)
    else:  # If triggered by /about command
        await update.message.reply_text(about_message, parse_mode="Markdown", disable_web_page_preview=True)


# 🔹 /star_user to maker user star member
async def star_user(update: Update, context: CallbackContext):
    if update.effective_user.id not in [5782873898]:  # Replace with your Admin ID
        await update.message.reply_text("❌ You are not authorized to do this!")
        return

    try:
        user_id = int(context.args[0])
        update_membership(user_id, "star")
        await update.message.reply_text(f"✅ User {user_id} is now a Star member!")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /star_user <user_id>")
        
        
        