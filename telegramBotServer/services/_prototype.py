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
            ret = customizedCallback(update.message)
            if type(ret) == tuple and len(ret) == 2:
                argv, msgtype = ret
            else:
                argv, msgtype = ret, "message"
            self.server.sender.send(
                msgtype,
                bot, 
                update.message.chat_id,
                argv
            )
        return ret

    def handler(self, message):
        raise NotImplementedError("Must override this.")
