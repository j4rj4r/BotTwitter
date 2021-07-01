# Standard libraries
import sys
import logging

# third party libraries
import tweepy
import yaml


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
        api = tweepy.API(auth)

        # Get Twitter User object and Create Table for each user
        user = api.me()
        return api, user

    def logging_configuration(self, logging_level):
        """
        Logging configuration function

        :return: None
        """
        logging.basicConfig(filename='logs/bot_twitter.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        root_logger = logging.getLogger()
        root_logger.setLevel(logging_level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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
