#!/usr/bin/env python3

from multiprocessing import *


def _botSender(msgtype, bot, chatid, argv):
    if msgtype == "message":
        bot.send_message(chat_id=chatid, **argv)
    elif msgtype == "photo":
        bot.send_photo(chat_id=chatid, **argv)
    else:
        print("Trying to send something without correct type specification.")

class TelegramBotSendingQueue:

    def __init__(self, processes=5):
        self.__pool = Pool(processes=processes)

    def send(self, msgtype, bot, chatid, argv):
        self.__pool.apply_async(_botSender, (msgtype, bot, chatid, argv))
