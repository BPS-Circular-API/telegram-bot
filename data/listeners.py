import telegram
import threading
import sqlite3
from telegram_bot_pagination import InlineKeyboardPaginator
from data.backend import console, get_list, amount_to_cache, get_png, get_circular_list, set_cached, get_cached


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


def get_circulars(_cats, final_dict):
    for item in _cats:
        res = get_circular_list(item)
        final_dict[item] = [res[i] for i in range(amount_to_cache)]

    set_cached(final_dict)

"""
def circular_checker():
    categories = ("ptm", "general", "exam")
    final_dict = {"general": [], "ptm": [], "exam": []}
    new_circular_categories = []
    new_circular_objects = []
    amount_to_cache = 5
    if amount_to_cache < 1:
        amount_to_cache = 1

    try:  # Try to get the cached data and make it a dict
        old_cached = dict(get_cached())

    except Exception as e:  # If it can't be gotten/can't be made into a dict (is None)
        console.warning(f"Error getting cached circulars : {e}")
        get_circulars(categories, final_dict)

        set_cached(final_dict)
        return

    if old_cached == {}:
        console.info("Cached is empty, setting it to the latest circular")
        get_circulars(categories, final_dict)
        return
    else:
        console.debug("Cache is not empty, checking for new circulars")

    for item in categories:
        res = get_circular_list(item)
        final_dict[item] = [res[i] for i in range(amount_to_cache)]

    get_circulars(categories, final_dict)

    console.debug('[Listeners] | ' + str(final_dict))
    console.debug('[Listeners] | ' + str(old_cached))

    for cat in categories:
        if not len(final_dict[cat]) == len(old_cached[cat]):
            get_circulars(categories, final_dict)
            console.info("The length of the circulars in a category is different, updating cache")
            return

    if final_dict != old_cached:  # If the old and new dict are not the same
        console.info("There's a new circular posted!")

        for circular_cat in categories:
            for i in range(len(final_dict[circular_cat])):
                if final_dict[circular_cat][i] not in old_cached[circular_cat]:
                    new_circular_categories.append(circular_cat)
                    new_circular_objects.append(final_dict[circular_cat][i])

        console.info(f"{len(new_circular_objects)} new circular(s) found")
        console.debug(new_circular_objects)

        for i in range(len(new_circular_objects)):
            notify(new_circular_categories[i], new_circular_objects[i])

    else:
        console.info("No new circulars")


def notify(cat, circular):
    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()
    # get users from db
    cur.execute("SELECT * FROM guild_notify")
    guilds = cur.fetchall()

    png = get_png(circular['link'])

    for guild in guilds:
        try:
            # send an image with caption to the guild
            bot.send_photo(guild[0], png, caption=f"*{circular['title']}*\n\n{circular['link']}", parse_mode='Markdown')    # TODO: Fix this

        except telegram.error.BadRequest:
            pass
"""


def error(update, context):
    """Log Errors caused by Updates."""
    console.warning('Update "%s" caused error "%s"', update, context.error)

# start circular checker as a daemon
# t = threading.Thread(target=circular_checker)
# t.daemon = True
# t.start()

