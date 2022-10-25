import configparser
import logging
import requests
import pickle
import sys
import sqlite3
from colorlog import ColoredFormatter

categories = ["general", "exam", "ptm"]

amount_to_cache = 1

# Loading config.ini
config = configparser.ConfigParser()

try:
    config.read('config.ini')
except Exception as e:
    print("Error reading the config.ini file. Error: " + str(e))
    sys.exit()


# Initializing the logger
def colorlogger():
    # disabler loggers
    for logger in logging.Logger.manager.loggerDict:
        logging.getLogger(logger).disabled = True
    logger = logging.getLogger()
    stream = logging.StreamHandler()
    log_format = "%(reset)s%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s"
    stream.setFormatter(ColoredFormatter(log_format))
    logger.addHandler(stream)
    return logger  # Return the logger


console = colorlogger()

try:
    # print all sections in the config file
    telegram_token: str = config.get('secret', 'telegram_token')
    log_level: str = config.get('main', 'log_level')
    base_api_url: str = config.get('main', 'base_api_url')
    amount_to_cache: int = config.getint('main', 'amount_to_cache')
    status_interval: int = config.getint('main', 'status_interval')

    embed_footer: str = config.get('discord', 'embed_footer')
    embed_color: int = int(config.get('discord', 'embed_color'), base=16)
    embed_title: str = config.get('discord', 'embed_title')
    embed_url: str = config.get('discord', 'embed_url')

except Exception as err:
    console.critical("Error reading the config.ini file. Error: " + str(err))
    sys.exit()

if log_level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    console.setLevel(log_level.upper())
else:
    console.warning(f"Invalid log level {log_level}. Defaulting to INFO.")
    console.setLevel("INFO")


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


def get_png(download_url: str) -> str or None:
    url = base_api_url + "getpng"
    params = {'url': download_url}

    request = requests.get(url, params=params)
    console.debug(request.json())

    if int(request.json()['http_status']) == 500:
        console.error("The API returned 500 Internal Server Error. Please check the API logs.")
        return
    return str(request.json()['data'])


def search(title: str) -> dict or None:
    url = base_api_url + "search"

    params = {'title': title}

    request = requests.get(url, params=params)
    console.debug(request.json())

    if int(request.json()['http_status']) == 500:
        console.error("The API returned 500 Internal Server Error. Please check the API logs.")
        return
    return request.json()['data']


def get_cached():
    # get dict from data/temp.pickle
    with open("./data/circular-cache.pickle", "rb") as f:
        return pickle.load(f)


def set_cached(obj):
    # set dict to data/temp.pickle
    with open("./data/circular-cache.pickle", "wb") as f:
        pickle.dump(obj, f)


def get_list():
    # get list from data/list.pickle
    with open("./data/list.pickle", "rb") as f:
        return pickle.load(f)


def set_list(obj):
    # set list to data/list.pickle
    with open("./data/list.pickle", "wb") as f:
        pickle.dump(obj, f)
