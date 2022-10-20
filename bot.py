from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from data.backend import *
from data.commands import *
from data.listeners import *

page_list = []



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Event Handlers
    dp.add_handler(CallbackQueryHandler(list_page_callback, pattern='^character#'))
    dp.add_error_handler(error)

    # Command Handlers
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("latest", latest_cmd))
    dp.add_handler(CommandHandler("list", list_cmd))
    dp.add_handler(CommandHandler("search", search_cmd))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Started")
    main()
