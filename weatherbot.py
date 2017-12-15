#!/usr/bin/env python3

import os
import sys
import logging
import yaml

from telegramBotServer import TelegramBotServer

from caeli.reports.report import ReportNWP
from caeli.commands.start import OnStartCommand
from caeli.commands.satimg import OnSatimgCommand


config = yaml.load(open(sys.argv[1], "r").read())
token = config["token"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

botServer = TelegramBotServer(token=token)
services = [
    OnStartCommand(botServer),
    OnSatimgCommand(botServer),
    ReportNWP(botServer),
]

print("Weather bot loaded and run...")
botServer.run()
