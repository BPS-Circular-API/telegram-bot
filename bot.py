import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from backend import *
from telegram_bot_pagination import InlineKeyboardPaginator

page_list = []


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def _latest(update, context):
    """Send the latest circulars."""
    category = context.args[0]
    info = get_latest_circular(category, cached=True)
    if info is None:
        update.message.reply_text("Error in fetching latest circulars.")
        return
    reply_text = ""
    reply_text += f"Latest `{category}` Circular:\n\n"

    reply_text += f"*Title*: `{info['title'].capitalize()}`\n"
    reply_text += f"*URL*: {info['link']}\n"

    png = get_png(info['link'])

    # send text and image in one message
    # update.message.reply_text(reply_text, parse_mode="Markdown")

    # send image with caption
    update.message.reply_photo(png, caption=reply_text, parse_mode="Markdown")


def _list(update, context):
    """Send the list of circulars."""
    category = context.args[0]
    raw_res = get_circular_list(category)
    if raw_res is None:
        update.message.reply_text("Error in fetching list of circulars.")
        return
    reply_text = ""
    reply_text += f"List of `{category}` Circulars:\n\n"

    loop_int = 1
    links = []
    titles = []

    for item in raw_res:
        titles.append(f"*{loop_int}*. `{item['title']}`")  # Add the title to the list
        links.append(f"{item['link']}")  # Add the link to the list
        loop_int += 1

    final_data = []
    temp = []

    count = 0

    for title, link in zip(titles, links):
        temp.append(f"{title}\n {link}\n\n")
        count += 1
        if count % 10 == 0:  # If the count is divisible by 10 (It has reached 10 fields)
            final_data.append(''.join(temp))  # Create a copy of the embed and add it to the list
            temp.clear()
        elif count == len(titles):
            final_data.append(''.join(temp))
            temp.clear()

    paginator = InlineKeyboardPaginator(
        len(titles) // 10 + 1,
        data_pattern='character#{page}'
    )

    # send the message with the paginator
    update.message.reply_text(
        text=final_data[0],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )
    global page_list
    page_list = final_data


def _search(update, context):
    args = context.args
    if len(args) == 0:
        update.message.reply_text("Please provide a search query.")
        return

    query = " ".join(args)
    res = search(query)
    if res is None:
        update.message.reply_text(f"*Circular Search*\n\n*Query*: `{query}`\n\n*Result*: No results found.", parse_mode="Markdown")
        return

    reply_text = f"*Circular Search*\n\n*Query*: `{query}`\n\n*Title*: `{res['title']}`\n*URL*: {res['link']}"
    png = get_png(res['link'])

    update.message.reply_photo(png, caption=reply_text, parse_mode="Markdown")


def list_page_callback(update, context):
    query = update.callback_query

    query.answer()

    page = int(query.data.split('#')[1])

    paginator = InlineKeyboardPaginator(
        len(page_list),
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


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CallbackQueryHandler(list_page_callback, pattern='^character#'))

    # Command Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("latest", _latest))
    dp.add_handler(CommandHandler("list", _list))
    dp.add_handler(CommandHandler("search", _search))

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Started")
    main()
