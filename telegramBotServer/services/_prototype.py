#!/usr/bin/env python3

from multiprocessing import *
import json

class _TelegramBotService:

    def __init__(self, server, handlerBuilder):
        self.server = server
        self.__pool = Pool()
        server.dispatcher.add_handler(handlerBuilder(
            self.__standardCallbackBuilder(self.handler)
        ))

    def __standardCallbackBuilder(self, customizedCallback):
        def ret(bot, update):
            argv = customizedCallback(update.message)
            self.server.sender.sendMessage(
                bot, 
                update.message.chat_id,
                argv
            )
        return ret

    def handler(self, message):
        raise NotImplementedError("Must override this.")
