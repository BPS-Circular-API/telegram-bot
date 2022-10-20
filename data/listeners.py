import telegram
from telegram_bot_pagination import InlineKeyboardPaginator
from data.backend import console, get_list


def list_page_callback(update, context):
    query = update.callback_query
    query.answer()

    page = int(query.data.split('#')[1])

    if query.data.split('#')[0] == "list_general":
        cat = "general"
    elif query.data.split('#')[0] == "list_ptm":
        cat = "ptm"
    elif query.data.split('#')[0] == "list_exam":
        cat = "exam"
    else:
        return

    page_list = get_list()[cat]

    paginator = InlineKeyboardPaginator(
        len(page_list),
        current_page=page,
        data_pattern=f"list_{cat}#" + '{page}'
    )

    try:
        query.edit_message_text(
            text=page_list[page - 1],
            reply_markup=paginator.markup,
            parse_mode='Markdown'
        )
    except telegram.error.BadRequest:
        pass


def error(update, context):
    """Log Errors caused by Updates."""
    console.warning('Update "%s" caused error "%s"', update, context.error)

