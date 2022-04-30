# Standard libraries
import sys
import logging
import random
import time
# third party libraries
import tweepy
import yaml


import BotTwitter.constants as const

class Helpers:
    def __init__(self):
        """
        Helpers class constructor
        """

    def ask_to_exit(self):
        """
        The user is asked if he wants to leave

        :return: Boolean
        """
        try:
            user_input = input('Type "STOP" to stop the application:\n')

            # Continue
            if user_input == "STOP":
                return True
            # Exit
            else:
                print('/!\\ Please type "STOP" to exit the bot execution /!\\')
                return False
        except Exception as e:
            return False

    def ask_menu(self):
        """
        The user is ask what to do with the bot
        """
        user_input = input("Select an option : \n[1] Start the Bot.\n[2] Stats of the bot.\n[3] Exit.\n")

        if user_input == "1":
            print('=========================================')
            print('= Bot will start in few seconds.        =')
            print('= Type "STOP" to exit the bot execution =')
            print('=========================================')
            return 'bot_start'
        elif user_input == "2":
            logging.error('Feature not implemented yet !')
            return 'bot_stats'
        # Exit
        else:
            sys.exit()

    def get_user(self, api_key, api_secret, access_token, access_secret, bearer_token):
        """
        this method allows you to authenticate to the api and retrieve the user object.

        :param api_key: api key
        :param api_secret: api secret
        :param access_token: access token
        :param access_secret: access secret
        :return: api
        :return: user
        """
        # Authenticate Key to use Twitter API
        api = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        # Authenticate with bearer token
        api_search = client = tweepy.Client(bearer_token)

        # getting the authenticated user's information
        user = api.get_me()
        user = user.data
        return api, api_search, user

    def logging_get_format(self, username=None):
        """
        Define the correct format for logs if we have the username of the current account.

        :return format : format for logging
        """
        if username is None:
            format='%(asctime)s - %(levelname)s \t- '+const.APP_NAME+' \t- %(message)s'
        else:
            format='%(asctime)s - %(levelname)s \t- ' + str(username) + ' \t-  %(message)s'
        return format

    def logging_configuration(self, logging_level=logging.INFO, filename='logs/bot_twitter.log', username=None):
        """
        Logging configuration function

        :param logging_level: logging level
        :filename: log file location and name
        :username: username of the account

        :return: None
        """
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # Create the logger with the specified name.
        format = self.logging_get_format(username)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(format)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging_level)
        stdout_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)


    def load_configuration(self, configuration_file):
        """
        this method allows you to load the configuration file and retrieve the variables.

        :param configuration_file: Name of the configuration file
        :return: out
        """
        # Load all configuration variables
        with open(configuration_file, 'r', encoding='utf8') as stream:
            out = yaml.load(stream, Loader=yaml.FullLoader)
        return out

# Utilities methods
def header():
    """
    This method display an header when the script start
    """
    logging.info('==\t=============================================================\t==')
    logging.info('==\t                   ' + const.APP_NAME + '                             \t==')
    logging.info('==\t                   version : ' + const.VERSION + '                         \t==')
    logging.info('==\t=============================================================\t==')

def wait(min=60, max=min, prefix=''):
    """
    Wait random time in second beetween min and max seconds, to have an not linear behavior and be more human.
    """
    random_sleep_time = random.randrange(min, max)
    logging.info(prefix +' - Sleep '+ str(random_sleep_time) +' seconds...')
    time.sleep(random_sleep_time)