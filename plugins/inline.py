from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import InlineQueryHandler, CallbackQueryHandler, CallbackContext
from database.filters_mdb import get_filter

# 🔍 Function for inline search with pagination
async def inline_search(update: Update, context: CallbackContext):
    query = update.inline_query.query.lower()
    if not query:
        return

    page = 0  # Default to page 0
    movies, has_next = get_filter(query, page)

    results = [
        InlineQueryResultArticle(
            id=movie["file_id"],
            title=movie["movie_name"],
            input_message_content=InputTextMessageContent(movie["movie_name"])
        )
        for movie in movies
    ]

    if results:
        # Add pagination buttons (Next if more results exist)
        buttons = []
        if has_next:
            buttons.append(InlineKeyboardButton("Next ⏭️", callback_data=f"page_{query}_{page+1}"))

        reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
        results.append(
            InlineQueryResultArticle(
                id="pagination",
                title="🔽 More Results 🔽",
                input_message_content=InputTextMessageContent("Use buttons to navigate."),
                reply_markup=reply_markup
            )
        )

    await update.inline_query.answer(results, cache_time=5)

# 🔹 Handle Pagination Button Clicks
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    if data[0] == "page":
        movie_name = data[1]
        page = int(data[2])

        movies, has_next = get_filter(movie_name, page)
        buttons = []

        # Add "Previous" button if not on first page
        if page > 0:
            buttons.append(InlineKeyboardButton("⏮️ Previous", callback_data=f"page_{movie_name}_{page-1}"))

        # Add "Next" button if more results exist
        if has_next:
            buttons.append(InlineKeyboardButton("Next ⏭️", callback_data=f"page_{movie_name}_{page+1}"))

        reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None

        # Edit inline message with new results
        await query.edit_message_text(
            text=f"🔍 Results for '{movie_name}' (Page {page + 1})",
            reply_markup=reply_markup
        )

# 🔹 Register inline handlers
def setup_handlers(app):
    app.add_handler(InlineQueryHandler(inline_search))
    app.add_handler(CallbackQueryHandler(button_handler, pattern=r"^page_.*"))