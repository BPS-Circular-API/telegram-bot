import telegram
import threading
import sqlite3
from telegram_bot_pagination import InlineKeyboardPaginator
from data.backend import console, get_list, get_png, get_circular_list, set_cached, get_cached, client
import pybpsapi


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
    new_circular_objects = {"general": [], "ptm": [], "exam": []}

    ptm = pybpsapi.CircularChecker('ptm', cache_method='database', db_name='data', db_path='./data', db_table='cache')
    general = pybpsapi.CircularChecker('general', cache_method='database', db_name='data', db_path='./data',
                                       db_table='cache')
    exam = pybpsapi.CircularChecker('exam', cache_method='database', db_name='data', db_path='./data', db_table='cache')

    ptm = ptm.check()
    general = general.check()
    exam = exam.check()

    if ptm:
        new_circular_objects["ptm"] = ptm
    if general:
        new_circular_objects["general"] = general
    if exam:
        new_circular_objects["exam"] = exam

    console.info(f"Found {len(new_circular_objects['general']) + len(new_circular_objects['ptm']) + len(new_circular_objects['exam'])} new circulars.")
    console.debug(f"New Circulars: {new_circular_objects}")

    if new_circular_objects["ptm"] or new_circular_objects["general"] or new_circular_objects["exam"]:
        for cat in new_circular_objects:
            if cat:
                for obj in new_circular_objects[cat]:
                    notify(cat, obj)

    else:
        console.debug(f"[Listeners] | No new circulars found.")


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
            console.warning(f"Error sending circular to {target[0]} Probably a deleted account")

        except Exception as e:
            console.warning(f"Error sending circular to {target[0]} : {e}")


def error(update, context):
    """Log Errors caused by Updates."""
    console.warning('Update "%s" caused error "%s"', update, context.error)


# start circular checker as a daemon
t = threading.Thread(target=circular_checker)
t.daemon = True
t.start()
