#!/usr/bin/env python3

from telegram.ext import MessageHandler
from ._prototype import _TelegramBotService

class TelegramBotMessageService(_TelegramBotService):
    
    def __init__(self, server, filters):
        _TelegramBotService.__init__(
            self,
            server,
            lambda func: MessageHandler(filters, func)
        )
