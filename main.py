# Standard libraries
import random
import sys
import time
from datetime import datetime, timedelta
import logging

# third party libraries
import tweepy
import yaml

# Local libraries
from bypass_antibot import BypassAntiBot
from manage_follow import ManageFollow, create_tables
from retweet_giveaway import RetweetGiveaway
from helper import Helper

# Configuration
VERSION = 3.0
CONFIGURATION_FILE = "configuration.yml"
Helper = Helper()

# Load all configuration variables
with open(CONFIGURATION_FILE, 'r', encoding="utf8") as stream:
    out = yaml.load(stream, Loader=yaml.FullLoader)
    words_to_search = out['words_to_search']
    accounts_to_tag = out['accounts_to_tag']
    words_to_blacklist_antibot = out['words_to_blacklist_antibot']
    sentence_for_tag = out['sentence_for_tag']
    hashtag_to_blacklist = [x.upper() for x in out['hashtag_to_blacklist']]
    giveaway_to_blacklist = [x.upper() for x in out['giveaway_to_blacklist']]
    accounts_to_blacklist = [w.replace('@', '') for w in out['accounts_to_blacklist']]
    list_account = out['accounts']
    bypass_antibot = out['bypass_antibot']
    like_giveaway = out['like_giveaway']
    comment_with_hashtag = out['comment_with_hashtag']
    max_giveaway = out['max_giveaway']
    logging_level = out['logging_level']
    flux_rss = out['flux_rss']

Helper.logging_configuration(logging_level)

# Main loop
while True:
    list_name = []
    for account in out['accounts']:
        for account_name, list_auth in account.items():
            try:
                # Extract API & ACCESS credentials
                api_key, api_secret, access_token, access_secret = list_auth
                api, user = Helper.get_user(api_key, api_secret, access_token, access_secret)

                create_tables(user)
                list_name.append("@" + user.screen_name)
                logging.info("Configuration completed for the account : %s", user.screen_name)

            except Exception as e:
                logging.error("Error with account : %s", account_name)
                logging.error(e)
                continue

    logging.info("-" * 40)
    # Add Accounts to Tag
    if accounts_to_tag:
        list_name += accounts_to_tag

    connection = 0
    # Looking for an account to find giveaway
    for account in out['accounts']:
        for account_name, list_auth in account.items():
            try:
                # If an account is available
                if connection == 1:
                    break
                api_key, api_secret, access_token, access_secret = list_auth
                api, user = Helper.get_user(api_key, api_secret, access_token, access_secret)
                connection = 1
            except:
                continue

    if connection == 0:
        logging.error("No account available!")
        sys.exit()
    else:
        rtgiveaway = RetweetGiveaway(api, user)
        giveaway_list = rtgiveaway.check_retweet(words_to_search,
                                                 accounts_to_blacklist,
                                                 hashtag_to_blacklist,
                                                 giveaway_to_blacklist,
                                                 comment_with_hashtag,
                                                 max_giveaway)

    for account in out['accounts']:
        for account_name, list_auth in account.items():
            try:
                # Thread here
                # Extract API & ACCESS credentials
                api_key, api_secret, access_token, access_secret = list_auth

                # Authenticate Key to use Twitter API
                auth = tweepy.OAuthHandler(api_key, api_secret)
                auth.set_access_token(access_token, access_secret)
                api = tweepy.API(auth)

                user = api.me()
                logging.info("-" * 40)
                logging.info("Launching the bot on : @%s", user.screen_name)

                managefollow = ManageFollow(user, api)
                managefollow.unfollow()

                rtgiveaway = RetweetGiveaway(api, user)
                rtgiveaway.manage_giveaway(giveaway_list, sentence_for_tag,
                                           list_name, hashtag_to_blacklist,
                                           managefollow, like_giveaway)

                # If the antibot bypass feature is activated
                if bypass_antibot:
                    bypass = BypassAntiBot(api, flux_rss, user)
                    bypass.bypass()

                logging.info("Sleeping for 30s...")
                time.sleep(30)

            except KeyboardInterrupt:
                Helper.ask_to_exit()

            except tweepy.TweepError as error:
                if error.api_code == 326 or error.api_code == 32:
                    logging.error("Connection error : %s", account_name)
                    continue
                else:
                    continue

    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        logging.info("Current time : %s", current_time)

        # Sleep if it's night time
        if 22 < now.hour < 2:
            waiting_time = 7 * 3600
        else:
            waiting_time = random.randrange(4000, 6000)

        logging.info("Waiting time before restarting bots : " + str(timedelta(seconds=waiting_time)))
        logging.info("-" * 40)

        time.sleep(waiting_time)
    except KeyboardInterrupt:
        Helper.ask_to_exit()
