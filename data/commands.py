from data.backend import get_latest_circular, get_circular_list, search, get_png, categories, get_list, set_list, client
from telegram_bot_pagination import InlineKeyboardPaginator
import sqlite3


def start_cmd(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hello! I am the BPS Circular Bot. Use /help to view the list of commands.')


def help_cmd(update, context):
    """Send a message when the command /help is issued."""
    reply_text = "**BPS Circular Bot**\n\n" \
                 "/latest `general`/`ptm`/`exam`: Sends the latest circular.\n" \
                 "/list `general`/`ptm`/`exam`: Sends the list of circulars.\n" \
                 "/search `search terms`: Searches for a circular.\n\n" \
                 "*Source Code*: https://bpsapi.rajtech.me/r/telegram-bot/\n" \
                 "Developed by [Raj Dave](t.me/@Nice_Creator)."

    update.message.reply_text(reply_text, parse_mode="Markdown")


# @client.message_handler(content_types=['latest'])
def latest_cmd(update, context):
    """Send the latest circulars."""
    try:
        if context.args[0][0] not in ['g', 'p', 'e']:
            raise ValueError
        category = "general" if context.args[0][0] == 'g' else "ptm" if context.args[0][0] == 'p' else "exam"
    except IndexError:
        update.message.reply_text("You are missing the category argument. Please include a category in your command. (`general`/`ptm`/`exam`)", parse_mode="Markdown")
        return
    except ValueError:
        update.message.reply_text("Please provide a valid category. (`general`/`ptm`/`exam`)", parse_mode="Markdown")
        return

    info = get_latest_circular(category, cached=True)
    png = get_png(info['link'])[0]     # Get the Circular's PNG

    if info is None:
        update.message.reply_text("Error in fetching latest circulars.")
        return

    reply_text = f"Latest `{category}` Circular:\n\n*Title*: `{info['title'].capitalize()}`\n*ID*: `{info['id']}`\n*URL*: {info['link']}"
    update.message.reply_photo(png, caption=reply_text, parse_mode="Markdown")


def list_cmd(update, context):
    """Send the list of circulars."""
    try:
        if context.args[0][0] not in ['g', 'p', 'e']:
            raise ValueError
        category = "general" if context.args[0][0] == 'g' else "ptm" if context.args[0][0] == 'p' else "exam"
    except IndexError:
        update.message.reply_text(
            "You are missing the category argument. Please include a category in your command. (`general`/`ptm`/`exam`)",
            parse_mode="Markdown")
        return
    except ValueError:
        update.message.reply_text("Please provide a valid category. (`general`/`ptm`/`exam`)", parse_mode="Markdown")
        return

    raw_res = get_circular_list(category)
    if raw_res is None:
        update.message.reply_text("Error in fetching list of circulars.")
        return

    loop_int = 1
    links = []
    titles = []

    for item in raw_res:
        titles.append(f"*{loop_int}*. \[{item['id']}] `{item['title']}`")  # Add the title to the list
        links.append(f"{item['link']}")  # Add the link to the list
        loop_int += 1

    final_data = []
    temp = []
    count = 0

    for title, link in zip(titles, links):
        temp.append(f"{title}\n {link}\n\n")
        count += 1
        if count % 10 == 0:  # If the count is divisible by 10 (It has reached 10 fields)
            temp.insert(0, f"List of `{category}` Circulars:\n\n")
            final_data.append(''.join(temp))  # Create a copy of the embed and add it to the list
            temp.clear()
        elif count == len(titles):
            temp.insert(0, f"List of `{category}` Circulars:\n\n")
            final_data.append(''.join(temp))
            temp.clear()

    del temp, count, links

    paginator = InlineKeyboardPaginator(
        len(titles) // 10 + 1,
        data_pattern=f'list_{category}#' + '{page}'
    )

    # send the message with the paginator
    update.message.reply_text(
        text=final_data[0],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )

    e = get_list()
    e[category] = final_data
    set_list(e)


def search_cmd(update, context):
    args = context.args
    if len(args) == 0:
        update.message.reply_text("Please provide a search query.")
        return

    query = " ".join(args).replace('"', '')
    res = search(query)
    if res is None:
        update.message.reply_text(f"*Circular Search*\n\n*Query*: `{query}`\n\n*Result*: No results found.", parse_mode="Markdown")
        return

    reply_text = f"*Circular Search*\n\n*Query*: `{query}`\n\n*Title*: `{res['title']}`\n*ID*: `{res['id']}`\n*URL*: {res['link']}"
    png = get_png(res['link'])[0]

    update.message.reply_photo(png, caption=reply_text, parse_mode="Markdown")


def guild_notify_cmd(update, context):
    """Send a message when the command /guild_notify is issued."""

    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()

    guild_id = update.message.chat.id
    cur.execute(f"SELECT * FROM guild_notify WHERE guild_id = {guild_id}")
    guilds = cur.fetchall()
    if not len(guilds) == 0:
        update.message.reply_text("You're already subscribed to the guild notifications.")
        return

    cur.execute(f"INSERT INTO guild_notify VALUES ({guild_id})")
    con.commit()

    update.message.reply_text("You have been subscribed to the guild notifications.")


def guild_unnotify_cmd(update, context):
    """Send a message when the command /guild_unnotify is issued."""
    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()
    guild_id = update.message.chat.id
    cur.execute(f"SELECT * FROM guild_notify WHERE guild_id = {guild_id}")
    guilds = cur.fetchall()
    if len(guilds) == 0:
        update.message.reply_text("You're not subscribed to the guild notifications.")
        return

    cur.execute(f"DELETE FROM guild_notify WHERE guild_id = {guild_id}")
    con.commit()

    update.message.reply_text("You have been unsubscribed from the guild notifications.")
