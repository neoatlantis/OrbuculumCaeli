#!/usr/bin/env python3

from telegramBotServer.services.message import *
from telegram.ext import Filters
import telegram

from ._report import report


class ReportNWP(TelegramBotMessageService):

    def __init__(self, server):
        TelegramBotMessageService.__init__(self, server, Filters.location)

    def handler(self, message):
        lat, lng = message.location.latitude, message.location.longitude
        text = report(lat, lng)
        return {
            "text": text,
            "parse_mode": telegram.ParseMode.HTML,
        }
