#!/usr/bin/env python3

from multiprocessing import *


def _botSendMessage(bot, chatid, argv):
    bot.send_message(chat_id=chatid, **argv)

class TelegramBotSendingQueue:

    def __init__(self, processes=5):
        self.__pool = Pool(processes=processes)

    def sendMessage(self, bot, chatid, argv):
        self.__pool.apply_async(_botSendMessage, (bot, chatid, argv))
