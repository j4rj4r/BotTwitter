import BotTwitter.alerter.discord
import BotTwitter.alerter.emailer
import BotTwitter.alerter.slack
import BotTwitter.alerter.telegram

from BotTwitter.alerter.common import AlerterFactory


def init_alerters(config):
    return AlerterFactory.create_from_config(config)
