#!/usr/bin/env python3

import os
import sys
import logging
import yaml

from telegramBotServer import TelegramBotServer
from caeli.report import ReportNWP
from caeli.cmdStart import OnStartCommand

config = yaml.load(open(sys.argv[1], "r").read())
token = config["token"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

botServer = TelegramBotServer(token=token)
services = [
    OnStartCommand(botServer),
    ReportNWP(botServer),
]
botServer.run()
