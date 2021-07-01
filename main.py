# Standard libraries
import logging
import random
import sys
import time
from datetime import datetime, timedelta

# third party libraries
import tweepy
import logging

# Local libraries
from BotTwitter.helpers import Helpers
from BotTwitter.action import Action
import BotTwitter.database_client

# Configuration
VERSION = 3.0
CONFIGURATION_FILE = 'configuration.yml'
DB_FILE = 'data.db'

helpers = Helpers()
# Load all configuration variables
config = helpers.load_configuration(CONFIGURATION_FILE)
# Configuration of the logging library
helpers.logging_configuration(config['logging_level'])

# if doesn't exist create database
dbman = BotTwitter.database_client.database(DB_FILE)
# if doesn't exist create users table
dbuser = dbman.Users()

while True:
    list_name = []
    mainaccount = []
    for account in config['accounts']:
        for account_name, list_auth in account.items():
            try:
                # Extract API & ACCESS credentials
                api_key, api_secret, access_token, access_secret = list_auth
                api, user = helpers.get_user(api_key, api_secret, access_token, access_secret)

                # Creation of the user in the database if it does not already exist
                if not dbuser.user_exists(user.id_str):
                    dbuser.add_user(user.id_str, user.screen_name)

                # Get account to retrieve the list of giveaways
                if not mainaccount:
                    mainaccount = [api, user]

                list_name.append('@' + user.screen_name)
                logging.info('Configuration completed for the account : %s', user.screen_name)

            except Exception as e:
                logging.error('Error with account : %s', account_name)
                logging.error(e)
                continue

    # If no account is available
    if not mainaccount:
        logging.error('No account available!')
        sys.exit()

    # Add Accounts to Tag
    if config['accounts_to_tag']:
        list_name += config['accounts_to_tag']
        # We don't want a duplicate
        list_name = list(set(list_name))

    action = Action(mainaccount[0], mainaccount[1], config)

    list_action = action.search_tweets()
    if not list_action:
        logging.error('There is no action to do!')
        sys.exit()
    time.sleep(100)
