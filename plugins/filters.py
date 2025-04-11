from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from database.filters_mdb import get_filter, get_movie_by_id
from database.user import is_verified
from plugins.verification import verify_user

# ✅ Movie Search with Verification
async def search_movie(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Check if user is verified
    if not is_verified(user_id):
        await verify_user(update, context)  # Correct function name
        return  

    query = update.message.text.strip()
    movies = get_filter(query, page_number=0)

    if not movies:
        await update.message.reply_text("❌ No movie founded or check your spelling")
        return

    keyboard = []
    for movie in movies:
        movie_name = movie.get("movie_name", "Unknown Title")[:50]
        movie_id = movie.get("_id", "")
        if movie_id:  # Only add if ID exists
            keyboard.append([
                InlineKeyboardButton(movie_name, callback_data=f"send|{movie_id}")
            ])

    if len(movies) == 8:
        keyboard.append([InlineKeyboardButton("⏭ Next", callback_data=f"page|{query}|1")])

    await update.message.reply_text("🔍 Search Results:", reply_markup=InlineKeyboardMarkup(keyboard))

# ✅ Pagination Handling
async def paginate_movies(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        _, movie_name, page = query.data.split("|", 2)
        page_number = int(page)
    except ValueError:
        return  

    movies = get_filter(movie_name, page_number)

    if not movies:
        await query.message.edit_text("❌ No more movies.")
        return

    keyboard = [
        [InlineKeyboardButton(movie["movie_name"][:50], callback_data=f"send|{movie['_id']}")]
        for movie in movies
    ]

    nav_buttons = []
    if page_number > 0:
        nav_buttons.append(InlineKeyboardButton("⏮ Previous", callback_data=f"page|{movie_name}|{page_number - 1}"))
    if len(movies) == 8:
        nav_buttons.append(InlineKeyboardButton("⏭ Next", callback_data=f"page|{movie_name}|{page_number + 1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    await query.message.edit_text("🔍 Search Results:", reply_markup=InlineKeyboardMarkup(keyboard))

# ✅ Send Selected Movie
async def send_selected_movie(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        _, movie_id = query.data.split("|", 1)
        movie = get_movie_by_id(movie_id)
    except Exception as e:
        await query.message.reply_text("❌ Error fetching movie.")
        return

    if not movie:
        await query.message.reply_text("❌ Movie not found in database.")
        return

    file_id = movie.get("file_id")
    movie_name = movie.get("movie_name", "Untitled")

    if not file_id or not isinstance(file_id, str):
        await query.message.reply_text("❌ Invalid or missing video file. Please contact admin.")
        return

    try:
        await query.message.reply_video(video=file_id, caption=f"🎬 {movie_name}")
    except Exception as e:
        await query.message.reply_text("❌ Failed to send video. File may have expired or is invalid.")
