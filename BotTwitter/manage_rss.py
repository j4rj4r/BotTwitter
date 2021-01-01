# Standard libraries
import sqlite3


class ManageRss:
    def __init__(self):
        """
        GestionRss constructor
        """

    def add_link(self, link):
        """
        Add a link to the database

        :param link String: link of an rss article
        """
        connection = sqlite3.connect('data.db')
        c = connection.cursor()
        c.execute('''INSERT INTO rss_links (link) VALUES (:link);''', (link,))
        c.close()
        connection.commit()

    def link_exist(self, link):
        """
        Returns true if the link exists in the database.

        :param link String: Link of an rss article
        """
        connection = sqlite3.connect('data.db')
        c = connection.cursor()
        c.execute('''SELECT * FROM rss_links WHERE link = ?;''', (link,))
        data = c.fetchall()
        # If this link exist or not
        if len(data) == 0:
            return False
        else:
            return True


def create_table_rss():
    """
    Create new tables to save the rss links.

    """
    connection = sqlite3.connect('data.db')
    c = connection.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rss_links
        (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, link text);''')
    c.close()
    connection.commit()
