# Standard libraries
import logging
import threading
import sys
from datetime import datetime, timedelta

# third party libraries
import tweepy

import BotTwitter.constants as const
from BotTwitter.action import Action
from BotTwitter.bypass_antibot import BypassAntiBot
from BotTwitter.helpers import wait


class Bot:
    def __init__(self, config, alerters, list_name, helpers):
        self.run = True
        self.config = config
        self.alerters = alerters
        self.list_name = list_name
        self.helpers = helpers

    # Worker 1 : Participate to giveaway
    def worker_participate_giveaways(self, user, api):
        """
        Run main process to participate to a giveaways
        """
        while self.run:  # Infinite loop
            try:
                # Set logs for the current user
                #self.helpers.logging_update_format(username=user.screen_name)
                self.helpers.logging_configuration(self.config['logging_level'],username=user.screen_name)
                # Initialize actions and unfollow giveaway > 2 month
                action = Action(self.config, self.list_name, user, api, self.alerters)
                action.manage_follow.unfollow() # Clear the follow list before to do any actions

                # We retrieve the list of actions to do
                list_action = action.search_tweets(api)
                # If there is no action
                if not list_action:
                    logging.error('There is no action to do!')

                # If the antibot bypass feature is activated, we bypass the antibot before to participate to a new giveaway
                if self.config["bypass_antibot"]:
                    bypass = BypassAntiBot(api, self.config["flux_rss"], user, self.config['words_to_blacklist'])
                    bypass.bypass()

                # Participate to giveaway
                action.manage_action(list_action)
            except Exception as e:
                logging.error('Error thread to participate to giveaways.')
                logging.debug(e)
                if e.api_code == 261:
                     # Send notification for the error code 261
                    alert_message = 'Error code 261 : Application blocked by Twitter.'
                    logging.error(alert_message)
                    if self.alerters:
                        self.alerters(subject='⚠ An issue with the account @'+self.user.screen_name+' need your attention ! ⚠',
                                    content=alert_message)
                    # Send notification for the end of the thread
                    alert_message = '/!\\ Stop participations for account ' + user.screen_name
                    logging.error(alert_message)
                    if self.alerters:
                        self.alerters(subject='🔴❌🔴 An issue with the account @'+self.user.screen_name+' need your attention ! 🔴❌🔴',
                                    content=alert_message)
                    self.run = False

            # Wait few seconds/minutes before to continue
            if self.run :
                wait(40, 180, "Worker 1 : Participate giveaways")

    # Worker 2 : Notify new private message receive
    def worker_detecting_mp(self ,user, api):
        """
        Notify new private message receive
        """
        while self.run: #Infinite loop
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
                is_not_old_message = (int(datetime.now().timestamp()) - 5 * 60) < int(int(dateMp) /1000)
                if is_not_old_message and self.config['be_notify_by_alerters'] and author_id is not last_author_id:
                    last_author_id = author_id
                    logging.info("Notification send : You have win a giveaway !")
                    # Retrive the giveaway
                    action = Action(self.config, self.list_name, user, api,  self.alerters)
                    tweetId, giveawayUsername, dateBot, tweetMessage = action.manage_giveaway.win(authorId=author_id)
                    if tweetId is not None:
                        # Notify user
                        self.alerters(subject='🎁 Congratulation @'+user.screen_name+', You probably won a giveaway ! 👏',
                                content='You just received a new private message on Twitter from @'+giveawayUsername+' this is probably about your participation'
                                        +'on '+str(dateBot)+' to the giveaway https://twitter.com/'+giveawayUsername+'/status/'+str(tweetId)+' !\n'
                                        +'-------------------- Giveaway details : --------------------\n'
                                        +'-- Participation date : '+str(dateBot) +'\n'
                                        +'-- Author of the giveaway : @'+str(giveawayUsername) +'\n'
                                        +'-- Open messages : https://twitter.com/messages/ \n'
                                        +'-- Giveaway URL : y https://twitter.com/'+giveawayUsername+'/status/'+str(tweetId) +'\n'
                                        +'-- Giveaway Message: \n'
                                        + tweetMessage + '\n'
                                        #+'\n-------------------- Private message : --------------------\n'
                                        #+ textMp
                                        +'\n------------------------------------------------------------\n'
                        )
                    else:
                        # Notify user with default message
                        self.alerters(subject='🎁 Congratulation @'+user.screen_name+', You probably won a giveaway ! 👏',
                                content='You just received a new private message on Twitter')
            except Exception as e:
                logging.error('Error thread to notify new private message.')
                logging.error(e)
            # Wait few seconds/minutes before to continue
            wait(20, 180, "Worker 2 : Direct message")


    def bot_start(self, user_information_list):
        # Step 2 :  Run Workers, 2 per account ( worker_detecting_mp, worker_participate_giveaways)
        # Each user do the actions, twitter will suggest different suggestion could be different
        threads = list()

        if self.alerters:
            self.alerters(subject='🚀 '+const.APP_NAME+' version '+const.VERSION+' is starting !  🚀', content='')
        # Start workers for every accounts
        for user_information in user_information_list:
            # Worker 1 : Participate to giveaways
            thread_participate = threading.Thread(target=self.worker_participate_giveaways, args=(user_information['user'], user_information['api']))
            threads.append(thread_participate)
            # Worker 2 : Monitoring of new private messages
            if self.alerters:
                thread_mp_notification = threading.Thread(target=self.worker_detecting_mp, args=(user_information["user"], user_information["api"],))
                threads.append(thread_mp_notification)

            # Start threads
            thread_participate.start()
            if self.alerters:
                thread_mp_notification.start()

        # Keep interactive way to stop the application
        while self.run:
            self.run = not self.helpers.ask_to_exit()
        logging.info("Bot will stop in few minutes !")
        # Stop all threads
        for thread in threads:
            thread.join()
        sys.exit(0)