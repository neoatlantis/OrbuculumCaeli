#!/usr/bin/env python3

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegramBotServer.services.command import *

class OnStartCommand(TelegramBotCommandService):

    def __init__(self, server):
        TelegramBotCommandService.__init__(self, server, 'start')
        self.__menu = ReplyKeyboardMarkup([
            ["/intel get latest intel!"],
            [KeyboardButton(
                "Weather forecast for your location!", 
                request_location=True
            )],
        ], resize_keyboard=True)

    def handler(self, message):
        text = "Welcome to Orbuculum Caeli bot!" + \
               "\n\nSend me a location to get weather forecasts, or \n" + \
               "Use /intel command to get latest intelligences."
        return {"text": text, "reply_markup": self.__menu }
