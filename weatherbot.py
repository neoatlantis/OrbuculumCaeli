#!/usr/bin/env python3

import os
import sys
import logging
import yaml
from _weather_report import report

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram

config = yaml.load(open(sys.argv[1], "r").read())
token = config["token"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

##############################################################################

def generateAnswer(location):
    lat, lng = location.latitude, location.longitude
    return report(lat, lng)

updater = Updater(token=token)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a bot, please talk to me!"
    )
dispatcher.add_handler(CommandHandler('start', start))


def query(bot, update):
    text = generateAnswer(update.message.location)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        parse_mode=telegram.ParseMode.HTML
    )

dispatcher.add_handler(MessageHandler(Filters.location, query))


updater.start_polling()
