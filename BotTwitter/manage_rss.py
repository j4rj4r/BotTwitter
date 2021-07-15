# Standard libraries
import datetime

import BotTwitter.constants as const
import BotTwitter.database_client as database_client


class ManageRss:
    def __init__(self, user):
        """
        GestionRss constructor
        """
        self.user = user
        self.database_path = const.DB_FILE
        self.database = database_client.database(self.database_path)
        self.database_rss = self.database.RSS()

    def add_link(self, link):
        """
        Add a link to the database

        :param link String: link of an rss article
        """
        self.database_rss.add_rss(self.user.id, str(link), datetime.datetime.now())

    def link_exist(self, link):
        """
        Returns true if the link exists in the database.

        :param link String: Link of an rss article
        """
        return self.database_rss.rss_exists(str(link))
