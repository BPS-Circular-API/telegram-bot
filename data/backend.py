import telegram.error
import configparser
import logging
import requests
import pickle
import sys
import sqlite3
from colorlog import ColoredFormatter
from telegram.ext import Updater
import pybpsapi

categories = ["general", "exam", "ptm"]

# Loading config.ini
config = configparser.ConfigParser()

try:
    config.read('config.ini')
except Exception as e:
    print("Error reading the config.ini file. Error: " + str(e))
    sys.exit()


# Initializing the logger
def colorlogger():
    logger = logging.getLogger()
    stream = logging.StreamHandler()
    log_format = "%(reset)s%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s"
    stream.setFormatter(ColoredFormatter(log_format))
    logger.addHandler(stream)
    return logger  # Return the logger


console = colorlogger()

# Get config

try:
    telegram_token: str = config.get('secret', 'telegram_token')
    log_level: str = config.get('main', 'log_level')
    base_api_url: str = config.get('main', 'base_api_url')

except Exception as err:
    console.critical("Error reading the config.ini file. Error: " + str(err))
    sys.exit()

# Config Checks

if log_level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    console.setLevel(log_level.upper())
else:
    console.warning(f"Invalid log level {log_level}. Defaulting to INFO.")
    console.setLevel("INFO")

if base_api_url[-1] != "/":     # Since some very bright people don't know how to fill in a config file
    base_api_url += "/"


def get_circular_list(category: str) -> tuple or None:
    url = base_api_url + "list"
    if category not in ["ptm", "general", "exam"]:
        return None

    params = {'category': category}

    request = requests.get(url, params=params)
    console.debug(request.json())
    if int(request.json()['http_status']) == 500:
        console.error("The API returned 500 Internal Server Error. Please check the API logs.")
        return
    return tuple(request.json()['data'])


def get_latest_circular(category: str, cached=False) -> dict or None:
    url = base_api_url + "latest" if not cached else base_api_url + "cached-latest"

    if category == "all":
        info = {}
        for i in categories:
            params = {'category': i}
            request = requests.get(url, params=params)
            res = request.json()
            info[i] = res['data']
    elif category in ['ptm', 'general', 'exam']:
        params = {'category': category}
        request = requests.get(url, params=params)
        try:
            info = request.json()['data']
        except Exception as errr:
            console.error(f"Error in get_latest_circular: {errr}")
            return
        if int(request.json()['http_status']) == 500:
            console.error("The API returned 500 Internal Server Error. Please check the API logs.")
            return
    else:
        return

    console.debug(info)
    return info


def get_png(download_url: str) -> list or None:
    url = base_api_url + "getpng"
    params = {'url': download_url}

    request = requests.get(url, params=params)
    console.debug(request.json())

    if int(request.json()['http_status']) == 500:
        console.error("The API returned 500 Internal Server Error. Please check the API logs.")
        return
    return list(request.json()['data'])


def search(title: str or int) -> dict or None:
    url = base_api_url + "search"

    params = {'title': title}

    request = requests.get(url, params=params)
    console.debug(request.json())

    if int(request.json()['http_status']) == 500:
        console.error("The API returned 500 Internal Server Error. Please check the API logs.")
        return
    return request.json()['data']


def get_cached() -> dict:
    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()
    cur.execute("SELECT data FROM cache WHERE title='circular'")
    return dict(pickle.loads(cur.fetchone()[0]))


def set_cached(obj: dict) -> None:
    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()
    cur.execute("UPDATE cache SET data=? WHERE title='circular'", (pickle.dumps(obj),))
    con.commit()
    con.close()


def get_list() -> dict:
    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()
    cur.execute("SELECT data FROM cache WHERE title='list'")
    return dict(pickle.loads(cur.fetchone()[0]))


def set_list(obj: dict) -> None:
    # set list to data/list.pickle
    con = sqlite3.connect("./data/data.db")
    cur = con.cursor()
    cur.execute("UPDATE cache SET data=? WHERE title='list'", (pickle.dumps(obj),))
    con.commit()
    con.close()


try:
    updater = Updater(telegram_token, use_context=True, request_kwargs={'read_timeout': 6, 'connect_timeout': 7})
except telegram.error.InvalidToken:
    console.critical("Invalid Telegram Token.")
    sys.exit()
except Exception as err:
    console.critical(f"Error: {err}")
    sys.exit()

client = updater.bot
