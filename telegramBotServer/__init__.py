#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram

from .sendingQueue import TelegramBotSendingQueue


class TelegramBotServer:

    def __init__(self, token=''):
        self.__updater = Updater(token=token)
        self.dispatcher = self.__updater.dispatcher
        self.sender = TelegramBotSendingQueue()

    def run(self):
        self.__updater.start_polling()
