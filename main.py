# Standard libraries
import logging
import random
import sys
import time
from datetime import datetime, timedelta

# third party libraries
import tweepy

# Local libraries
import BotTwitter.constants as const
import BotTwitter.database_client
from BotTwitter.helpers import Helpers, header, wait
from BotTwitter.alerter import init_alerters
from BotTwitter.bot import Bot

# Step 0 : Initialization

# Configuration
const.init()

helpers = Helpers()
# Load all configuration variables
config = helpers.load_configuration(const.CONFIGURATION_FILE)
# Configuration of the logging library
helpers.logging_configuration(config['logging_level'])
# Display header
header()
logging.info('Starting bot ...')
# Configuration of alert system
if config['be_notify_by_alerters']:
    alerters = init_alerters(config)
else:
    alerters = None
# if doesn't exist create database
dbman = BotTwitter.database_client.database(const.DB_FILE)
# if doesn't exist create users table
dbuser = dbman.Users()

# Step 1 : Extract one time, user and api from different account in configuration file
list_name = []
user_information_list = []
for account in config['accounts']:
    for account_name, list_auth in account.items():
        try:
            # Extract API & ACCESS credentials
            api_key, api_secret, access_token, access_secret = list_auth
            api, user = helpers.get_user(api_key, api_secret, access_token, access_secret)

            # Creation of the user in the database if it does not already exist
            if not dbuser.user_exists(user.id_str):
                dbuser.add_user(user.id_str, user.screen_name)

            list_name.append('@' + user.screen_name)
            user_information_list.append({'api': api, 'user': user})
            logging.info('Configuration completed for the account : %s', user.screen_name)

        except Exception as e:
            logging.error('Error with account : %s', account_name)
            logging.error(e)
            continue

# Add Accounts to Tag
if config['accounts_to_tag']:
    list_name += config['accounts_to_tag']
    # We don't want a duplicate
    list_name = list(set(list_name))

#
bot = Bot(config, alerters, list_name, helpers)
# Check run options
if len(sys.argv) > 1 and sys.argv[1] == '--standelone':
    logging.info("Mode : Standelone")
    bot.bot_start(user_information_list)
else:
    logging.info("Mode : Interactive")
    command = helpers.ask_menu()
    if command == 'bot_start':
        bot.bot_start(user_information_list)
