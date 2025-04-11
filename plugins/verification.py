import requests
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from database.user import update_verification, is_verified

# Your URL Shortener API Key
URL_SHORTENER_API = "https://api.modijiurl.com/api?api=224d742960cf7efa4752e13f3cade017cac1728e&url="

# ✅ Generate Verification Link
def generate_verification_link(user_id):
    """Generate a unique verification URL for the user."""
    redirect_url = f"https://t.me/FlickWiz_Bot?start=verify_{user_id}"

    try:
        response = requests.get(f"{URL_SHORTENER_API}{redirect_url}").json()
        short_url = response.get("shortenedUrl")

        return short_url if short_url else redirect_url  # Fallback if shortening fails
    except Exception as e:
        print(f"URL Shortener Error: {e}")
        return redirect_url  # Use direct URL as a fallback

# ✅ Ask User to Verify
async def verify_user(update: Update, context: CallbackContext):
    """Prompt user to verify via URL shortener."""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    if is_verified(user_id):
        await update.message.reply_text("✅ You are already verified!")
        return

    # Generate short link
    verification_url = generate_verification_link(user_id)

    # Send verification prompt
    keyboard = [
        [InlineKeyboardButton("🔗 Verify Now", url=verification_url)],
        [InlineKeyboardButton("ℹ️ How to Verify", url="https://youtu.be/70sDHMlT34E?si=oolhl0N7E2TUXRLn")]
    ]
    await update.message.reply_text(
        "🔒 To access movie search, you must verify every 24 hours.\n\n"
        "Click the button below and return to the bot after completing verification.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



# ✅ Handle /verify Command

async def confirm_verification(update: Update, context: CallbackContext):
    """Mark user as verified after they complete verification."""
    user_id = update.message.from_user.id
    print(f"Confirming verification for: {user_id}")  # Debugging

    if is_verified(user_id):
        await update.message.reply_text("✅ You are already verified!")
        return

    update_verification(user_id)
    
    # Double-check if it updated
    from database.users import users_col
    user = users_col.find_one({"user_id": user_id})
    print(f"Updated user data: {user}")  # Debugging

    await update.message.reply_text("✅ Verification successful! You can now search and get movies.")