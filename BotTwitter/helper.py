# Standard libraries
import sys
import logging

# third party libraries
import tweepy

class Helper:
    def __init__(self):
        """
        HelperFunctions class constructor
        """

    def ask_to_exit(self):
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
        # Authenticate Key to use Twitter API
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        # Get Twitter User object and Create Table for each user
        user = api.verify_credentials()
        return api, user

    def logging_configuration(self, logging_level):
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