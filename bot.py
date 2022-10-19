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
    print(context)
    print(context.args)
    info = get_latest_circular(category, cached=True)
    print(info)
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





def error(update, context):
    """Log Errors caused by Updates."""
    console.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # dp.add_handler(CallbackQueryHandler(list_page_callback, pattern='^character#'))

    # Command Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("latest", _latest))
    # dp.add_handler(CommandHandler("list", _list))

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Started")
    main()
