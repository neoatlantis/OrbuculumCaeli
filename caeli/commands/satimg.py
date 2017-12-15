#!/usr/bin/env python3

from telegram import ReplyKeyboardMarkup
from telegramBotServer.services.command import *
import re

class OnSatimgCommand(TelegramBotCommandService):

    baseUrl = "http://intell.neoatlantis.org/"
    products = [
        ("HMWR-8 Eastern China Clouds",     "h8images-eastern_china_band_12/latest.gif"),
        ("Met-10 Europe & Africa",          "meteosat10images-africa_northern_overview_eumetsat_dust/latest.jpg"),
    ]

    def __init__(self, server):
        TelegramBotCommandService.__init__(self, server, 'satimg')
        self.__menu = ReplyKeyboardMarkup([
            ["/satimg #%d: %s" % (i+1, self.products[i][0])]
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
            ret["photo"] = self.baseUrl + self.products[imgid][1]
            return ret, "photo"

        ret["text"] = "Please select a product you want to check out."
        return ret 
