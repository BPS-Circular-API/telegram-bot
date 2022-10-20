from telegram_bot_pagination import InlineKeyboardPaginator
from data.backend import console, get_list


def list_page_callback(update, context):
    query = update.callback_query
    print(query.data)
    query.answer()

    page = int(query.data.split('#')[1])

    if query.data.split('#')[0] == "list_general":
        page_list = get_list()['general']
    elif query.data.split('#')[1] == "list_ptm":
        page_list = get_list()['ptm']
    elif query.data.split('#')[1] == "list_exam":
        page_list = get_list()['exam']
    else:
        return

    paginator = InlineKeyboardPaginator(
        len(page_list) // 10 + 1,
        current_page=page,
        data_pattern='character#{page}'
    )

    query.edit_message_text(
        text=page_list[page - 1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )


def error(update, context):
    """Log Errors caused by Updates."""
    console.warning('Update "%s" caused error "%s"', update, context.error)

