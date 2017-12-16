#!/usr/bin/env python3

import re
import random
import datetime
from telegram import ReplyKeyboardMarkup
from telegramBotServer.services.command import *

INTELBASE = "http://intell.neoatlantis.org/"

class OnIntelCommand(TelegramBotCommandService):

    products = [
        ("HMWR-8 Eastern China Clouds",\
            INTELBASE + "h8images-eastern_china_band_12/latest.gif"),
        ("Met-10 Europe & Africa", \
            INTELBASE + "meteosat10images-africa_northern_overview_eumetsat_dust/latest.jpg"),
        ("Met-10 Northern Atlantic", \
            INTELBASE + "meteosat10images-atlantic_northern_overview_eumetsat_dust/latest.jpg"),
        ("Europe Weather Warnings", \
            "http://www.unwetterzentrale.de/images/map/europe_index.png"),

    ]

    def __getTimestamp(self):
        # Used for caching with respect to Telegram. The timestamp remains
        # unchanged for every 5 mintues rather than every request as with a
        # random number.
        now = datetime.datetime.utcnow()
        return "%d%d%d%d%d" % (
            now.year,
            now.month,
            now.day,
            now.hour,
            (round(now.minute / 5) * 5) % 60,
        )

    def __init__(self, server):
        TelegramBotCommandService.__init__(self, server, 'intel')
        self.__menu = ReplyKeyboardMarkup([
            ["/intel #%d: %s" % (i+1, self.products[i][0])]
            for i in range(0, len(self.products))
        ], resize_keyboard=True)

    def handler(self, message):
        ret = { "reply_markup": self.__menu, }
        # Analyze text, if text includes a name of one of our products, display
        # the image. Otherwise just show the menu again.
        imgid = -1
        try:
            text = message["text"]
            found = re.search("#([0-9]{1,}):", text)
            if found:
                imgid = int(found.group(1)) - 1
        except:
            imgid = -1
        if imgid >= 0 and imgid < len(self.products):
            # Returns image as specified by `imgid`.
            anticache = "?__wtf=%s" % self.__getTimestamp()
            ret["photo"] = self.products[imgid][1] + anticache 
            return ret, "photo"

        ret["text"] = "Please select a product you want to check out."
        return ret 
