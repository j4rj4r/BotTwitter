# Standard libraries
import random
import sys
import time
from datetime import datetime

# third party libraries
import tweepy
import yaml

# Local libraries
from bypass_antibot import BypassAntiBot
from manage_follow import ManageFollow, create_tables
from retweet_giveaway import RetweetGiveaway


# Helper Functions
def ask_to_exit():
    print('''[1] Next account | [2] Exit ''')
    user_input = input("Your choice (by default 2): ")

    # Continue
    if user_input == "1":
        pass
    # Exit
    else:
        sys.exit()
    pass


def get_user(api_key, api_secret, access_token, access_secret):
    # Authenticate Key to use Twitter API
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    # Get Twitter User object and Create Table for each user
    user = api.me()
    return api, user


# Configuration
VERSION = 3.0
CONFIGURATION_FILE = "configuration.yml"


# Load all configuration variables
with open(CONFIGURATION_FILE, 'r') as stream:
    out = yaml.load(stream, Loader=yaml.FullLoader)
    words_to_search = out['words_to_search']
    accounts_to_tag = out['accounts_to_tag']
    words_to_blacklist_antibot = out['words_to_blacklist_antibot']
    sentence_for_tag = out['sentence_for_tag']
    hashtag_to_blacklist = [x.upper() for x in out['hashtag_to_blacklist']]
    giveaway_to_blacklist = [x.upper() for x in out['giveaway_to_blacklist']]
    accounts_to_blacklist = [w.replace('@', '') for w in out['accounts_to_blacklist']]
    list_account = out['accounts']


# Main loop
while True:
    try:
        list_name = []
        for account in out['accounts']:
            for account_name, list_auth in account.items():
                try:
                    # Extract API & ACCESS credentials
                    api_key, api_secret, access_token, access_secret = list_auth
                    api, user = get_user(api_key, api_secret, access_token, access_secret)

                    create_tables(user)
                    list_name.append("@" + user.screen_name)
                    print("Configuration completed for the account : ", user.screen_name)

                except Exception as e:
                    print("Error with account : ", account_name)
                    print(e)


        # Add Accounts to Tag
        list_name += accounts_to_tag

        # Get the First User Twitter Object
        first_account_cred = list(list_account[0].values())[0]
        api_key, api_secret, access_token, access_secret = first_account_cred
        api, user = get_user(api_key, api_secret, access_token, access_secret)

        # TODO: Refactor Elifs
        rtgiveaway = RetweetGiveaway(api, user)
        giveaway_list = rtgiveaway.check_retweet(words_to_search,
                                                 accounts_to_blacklist,
                                                 hashtag_to_blacklist,
                                                 giveaway_to_blacklist)

        for account in out['accounts']:
            for account_name, list_auth in account.items():
                try:
                    # Extract API & ACCESS credentials
                    api_key, api_secret, access_token, access_secret = list_auth

                    # Authenticate Key to use Twitter API
                    auth = tweepy.OAuthHandler(api_key, api_secret)
                    auth.set_access_token(access_token, access_secret)
                    api = tweepy.API(auth)

                    user = api.me()
                    account = user.screen_name
                    print("-" * 40)
                    print("Launching the bot on  : @", user.screen_name)

                    managefollow = ManageFollow(user, api)
                    managefollow.unfollow()
                    # Petit check avant le process de concours
                    bypass = BypassAntiBot(api, account)
                    bypass.bypass()
                    # TODO: Refactor if else
                    rtgiveaway = RetweetGiveaway(api, user)
                    rtgiveaway.manage_giveaway(giveaway_list, sentence_for_tag,
                                               list_name, hashtag_to_blacklist,
                                               managefollow)
                    bypass = BypassAntiBot(api, account)
                    bypass.bypass()
                    time.sleep(30)

                except KeyboardInterrupt:
                    ask_to_exit()

                except tweepy.TweepError as error:
                    if error.api_code == 326 or error.api_code == 32:
                        print("Connection error : " + account_name)
                    else:
                        print(error)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current time : " + current_time)

        # Sleep if it's night time
        if now.hour > 23:
            waiting_time = 10 * 3600
        else:
            waiting_time = random.randrange(4000, 6000)
        print("Waiting time before restarting bots : " + str(waiting_time/3600) + " h")
        print("-" * 40)

        time.sleep(waiting_time)

    # if ctrl-c
    except KeyboardInterrupt:
        ask_to_exit()
    except tweepy.TweepError as error:
        if error.api_code == 326 or error.api_code == 32:
            print("Connection error : " + account_name)
        else:
            print(error)
