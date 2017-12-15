#!/usr/bin/env python3

from telegram.ext import CommandHandler
from ._prototype import _TelegramBotService

class TelegramBotCommandService(_TelegramBotService):
    
    def __init__(self, server, command):
        _TelegramBotService.__init__(
            self,
            server,
            lambda func: CommandHandler(command, func)
        )
