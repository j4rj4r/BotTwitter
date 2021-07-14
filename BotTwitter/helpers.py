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

        :return: None
        """
        print('''[1] Next account | [2] Exit ''')
        user_input = input("Your choice (by default 2): ")

        # Continue
        if user_input == "1":
            pass
        # Exit
        else:
            sys.exit()
        pass

    def get_user(self, api_key, api_secret, access_token, access_secret):
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
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        # calling the api
        api = tweepy.API(auth, wait_on_rate_limit=True)
        # getting the authenticated user's information
        user = api.me()
        return api, user

    def logging_get_format(self, username=None):
        """
        Define the correct format for logs if we have the username of the current account.

        :return format : format for logging
        """
        if username is None:
            format='%(asctime)s - %(levelname)s - '+const.APP_NAME+'\t- %(message)s'
        else:
            format='%(asctime)s - %(levelname)s - ' + str(username) + '\t-  %(message)s'
        return format

    def logging_update_format(self, username=None):
        """
        Update logging format if an username is specify
        """
        format = self.logging_get_format(username)
        formatter = logging.Formatter(format)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()  # root logger
        for hdlr in root_logger.handlers[:]: # remove all old handlers
            root_logger.removeHandler(hdlr)
        root_logger.addHandler(handler) # set the new handler


    def logging_configuration(self, logging_level=logging.INFO, filename='logs/bot_twitter.log'):
        """
        Logging configuration function

        :param logging_level: logging level
        :filename: log file location and name
        :username: username of the account

        :return: None
        """
        format = self.logging_get_format()

        logging.basicConfig(filename=filename,
                            level=logging.INFO,
                            format=format)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging_level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    def load_configuration(self, configuration_file):
        """
        this method allows you to load the configuration file and retrieve the variables.

        :param configuration_file: Name of the configuration file
        :return: out
        """
        # Load all configuration variables
        with open(configuration_file, 'r', encoding="utf8") as stream:
            out = yaml.load(stream, Loader=yaml.FullLoader)
        return out

# Utilities methods
def header():
    """
    This method display an header when the script start
    """
    print('==\t=============================================================\t==')
    print('==\t                   ' + const.APP_NAME + '                             \t==')
    print('==\t                   version : ' + const.VERSION + '                         \t==')
    print('==\t=============================================================\t==\n')

def wait(min=60, max=min, name=''):
    """
    Wait random time in second beetween min and max seconds, to have an not linear behavior and be more human.
    """
    random_sleep_time = random.randrange(min, max)
    print(name+" - Sleep %s seconds.", str(random_sleep_time))
    time.sleep(random_sleep_time)