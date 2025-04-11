import asyncio
import logging
import os
import signal
import sys
import traceback
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from config import BOT_TOKEN, ADMIN_ID
from plugins.functions import start, help, about, star_user
from plugins.filters import search_movie, send_selected_movie, paginate_movies
from plugins.verification import verify_user
from database.user import is_verified

# Setup Logging
logging.basicConfig(
    filename="bot_errors.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.ERROR
)
    
async def error_handler(update: Update, context):
    """Handles errors and sends them to admin."""
    error_trace = "".join(traceback.format_exception(None, context.error, context.error.__traceback__))
    error_msg = f"🚨 Bot Crashed!\n\n```{error_trace}```"

    logging.error(error_msg)  # Log to file

    # Send error report to admin
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=error_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Failed to send error message: {e}")  # Debugging

async def stop_loop(update: Update, context):
    """Stops the loop and prevents auto-restart"""
    if update.message.from_user.id == 5782873898:
        with open("stop_loop.txt", "w") as f:
            f.write("stop")
        await update.message.reply_text("🛑 Bot loop has been stopped.")
        
        # Simulate Ctrl + C to stop the bot
        os.kill(os.getpid(), signal.SIGINT)  
    else:
        await update.message.reply_text("❌ You are not authorized to stop the bot.")

# ✅ Middleware: Check User Verification
async def check_verification(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    if not is_verified(user_id):
        await verify_user(update, context)
        return False  # Stop further execution
    
    return True  # Continue with the command

def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()

        # Register Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help))
        app.add_handler(CommandHandler("about", about))
        app.add_handler(CommandHandler("star_user", star_user))
        app.add_handler(CommandHandler("stoploop", stop_loop))
        app.add_handler(CommandHandler("verify", verify_user))  # Manually trigger verification
        app.add_handler(CallbackQueryHandler(send_selected_movie, pattern=r"^send\|"))
        app.add_handler(CallbackQueryHandler(paginate_movies, pattern=r"^page\|"))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

        # Register Error Handler
        app.add_error_handler(error_handler)

        print("✅ User Bot is running...")
        app.run_polling()

    except Exception:
        crash_error = f"🚨 BOT CRASHED!\n\n{traceback.format_exc()}"
        logging.error(crash_error)

        # Send error to admin asynchronously
        async def send_crash_report():
            bot = Bot(token=BOT_TOKEN)
            try:
                await bot.send_message(chat_id=ADMIN_ID, text=crash_error)
            except Exception as e:
                logging.error(f"Failed to notify admin: {e}")

        asyncio.run(send_crash_report())  # Properly await the async function

        sys.exit(1)  # Stop execution

if __name__ == "__main__":
    main()