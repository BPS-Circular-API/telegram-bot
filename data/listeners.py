import telegram
import threading
import sqlite3
from telegram_bot_pagination import InlineKeyboardPaginator
from data.backend import console, get_list, get_png, get_circular_list, set_cached, get_cached, client


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
        final_dict[item] = get_circular_list(item)

    set_cached(final_dict)


def circular_checker():
    categories = ("ptm", "general", "exam")
    final_dict = {"general": [], "ptm": [], "exam": []}
    new_circular_objects = {"general": [], "ptm": [], "exam": []}

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
        final_dict[item] = get_circular_list(item)

    get_circulars(categories, final_dict)

    console.debug('[Listeners] | ' + str(final_dict))
    console.debug('[Listeners] | ' + str(old_cached))

    if final_dict != old_cached:  # If the old and new dict are not the same
        console.info("There's a new circular posted!")

        for circular_cat in categories:
            new_circular_objects[circular_cat] = [i for i in final_dict[circular_cat] if
                                                  i not in old_cached[circular_cat]]

        console.info(f"{(sum(len(v) for v in new_circular_objects.values()))} new circular(s) found")
        console.debug(new_circular_objects)

        for cat in categories:
            for circular in new_circular_objects[cat]:
                console.debug(circular)
                notify(cat, circular)

    else:
        console.info("No new circulars")


def notify(cat, circular):
    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()
    # get users from db
    cur.execute("SELECT * FROM notify")
    targets = cur.fetchall()

    png = get_png(circular['link'])[0]

    for target in targets:
        try:
            client.send_photo(
                target[0], photo=png, caption=
                    f"New Circular in *{cat.capitalize()}*\n"
                    f"\n"
                    f"*Title*: `{circular['title']}`\n"
                    f"*ID*: `{circular['id']}`\n"
                    # f"\n"
                    f"*URL*: {circular['link']}",
                parse_mode='Markdown')

            console.info(f"Sent circular to {target[0]}")

        except telegram.error.BadRequest:
            pass

        except Exception as e:
            console.warning(f"Error sending circular to {target[0]} : {e}")


def error(update, context):
    """Log Errors caused by Updates."""
    console.warning('Update "%s" caused error "%s"', update, context.error)


# start circular checker as a daemon
t = threading.Thread(target=circular_checker)
t.daemon = True
t.start()
