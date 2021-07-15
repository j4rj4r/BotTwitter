# Standard libraries
import logging
import random
import sys
import time
from datetime import datetime, timedelta

# third party libraries
import tweepy
import threading

# Local libraries
import BotTwitter.constants as const
import BotTwitter.database_client
from BotTwitter.helpers import Helpers, header, wait
from BotTwitter.action import Action
from BotTwitter.bypass_antibot import BypassAntiBot
from BotTwitter.alerter import init_alerters


# Step 0 : Initialization

# Configuration
const.init()

helpers = Helpers()
header()
# Load all configuration variables
config = helpers.load_configuration(const.CONFIGURATION_FILE)
# Configuration of the logging library
helpers.logging_configuration(config['logging_level'])
# Configuration of alert system
alerters = init_alerters(config)

# if doesn't exist create database
dbman = BotTwitter.database_client.database(const.DB_FILE)
# if doesn't exist create users table
dbuser = dbman.Users()

# Step 1 : Extract one time, user and api from different account in configuration file
mainaccount = None
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

            # Get account to retrieve the list of giveaways
            if not mainaccount:
                mainaccount = api

            list_name.append('@' + user.screen_name)
            user_information_list.append({'api': api, 'user': user})
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

    # Worker 1 : Participate to giveaway
    def worker_participate_giveaways(user_information):
        """
        Run main process to participate to a giveaways
        """
        while  True : # Infinite loop
            try:
                # Set logs for the current user
                helpers.logging_update_format(username=user_information["user"].screen_name)

                # Initialize actions and unfollow giveaway > 2 month
                action = Action(config, list_name, user_information["user"], user_information["api"])
                action.manage_follow.unfollow() # Clear the follow list before to do any actions

                # We retrieve the list of actions to do
                list_action = action.search_tweets(mainaccount)
                # If there is no action
                if not list_action:
                    logging.error('There is no action to do!')

                # If the antibot bypass feature is activated, we bypass the antibot before to participate to a new giveaway 
                if config['bypass_antibot']:
                    bypass = BypassAntiBot(user_information['api'], config['flux_rss'], user_information['user'])
                    bypass.bypass()

                # Participate to giveaway
                action.manage_action(list_action)

            except Exception as e:
                logging.error('Error thread to participate to giveaways.')
                logging.error(e)

            # Wait few seconds/minutes before to continue
            wait(100, 200, 'Participate giveaways')

    # Worker 2 : Notify new private message receive
    def worker_detecting_mp(api, user):
        while True: #Infinite loop
            def get_last_received(my_mps):
                for mp in my_mps:
                    if str(mp.message_create['target']['recipient_id']) == str(user.id):
                        # return infos we encounter the first received message object
                        text = mp.message_create['message_data']['text']
                        author_id = mp.message_create['sender_id']
                        date = mp.created_timestamp
                        return date, author_id, text


            last_author_id = ''
            try:
                my_mps = api.list_direct_messages()
                dateMp, author_id, textMp = get_last_received(my_mps)
                # If the message have been receive during last 5 mins, we notify use alerts.
                is_not_old_message = (int(datetime.now().timestamp()) - 5*60) < int(dateMp)
                if is_not_old_message and config['be_notify_by_alerters'] and author_id is not last_author_id:
                    last_author_id = author_id
                    logging.info('Notification send : You have win a giveaway !')
                    # Retrive the giveaway
                    action = Action(config, list_name, user_information['user'], user_information['api'])
                    tweetId, giveawayUsername, dateBot, tweetMessage = action.manage_giveaway.win(authorId=author_id)
                    # Notify user
                    alerters(subject=f'🎁 Congratulation @{user.screen_name}, You probably won a giveaway ! 👏',
                            content='You just received a new private message on Twitter from @'+giveawayUsername+' this is probably about your participation'
                                    +'on '+str(dateBot)+' to the giveaway https://twitter.com/'+giveawayUsername+'/status/'+str(tweetId)+' !\n'
                                    +'-------------------- Giveaway details : --------------------\n'
                                    +'-- Participation date : '+str(dateBot) +'\n'
                                    +'-- Author of the giveaway : @'+str(giveawayUsername) +'\n'
                                    +'-- Open messages : https://twitter.com/messages/ \n'
                                    +'-- Giveaway URL : y https://twitter.com/'+giveawayUsername+'/status/'+str(tweetId) +'\n'
                                    +'-- Giveaway Message: \n'
                                    + tweetMessage + '\n'
                                    #+'\n--------------------Private message : --------------------\n'
                                    #+ textMp
                                    +'\n------------------------------------------------------------\n'
                    )
            except Exception as e:
                logging.error('Error thread to notify new private message.')
                logging.error(e)
            # Wait few seconds/minutes before to continue
            wait(180, 250, 'Direct message')


# Step 2 :  Run Workers 2 per account ( worker_detecting_mp, worker_participate_giveaways)
# Each user do the actions, twitter will suggest different suggestion could be different
threads = list()
for user_information in user_information_list:
    # Worker 1 : Participate to giveaways
    #worker_participate_giveaways(user_information)
    thread_participate = threading.Thread(target=worker_participate_giveaways, args=(user_information,))
    threads.append(thread_participate)
    # Worker 2 : Monitoring of new private messages
    #worker_detecting_mp(user_information["api"], user_information["user"])
    thread_mp_notification = threading.Thread(target=worker_detecting_mp, args=(user_information["api"], user_information["user"],))
    threads.append(thread_mp_notification)

    # Start threads
    thread_participate.start()
    thread_mp_notification.start()