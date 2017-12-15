#!/usr/bin/env python3

from telegramBotServer.services.command import *

class OnStartCommand(TelegramBotCommandService):

    def __init__(self, server):
        TelegramBotCommandService.__init__(self, server, 'start')

    def handler(self, message):
        return {"text": "I'm a bot, please talk to me!"}
