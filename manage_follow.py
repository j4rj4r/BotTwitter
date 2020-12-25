# Standard libraries
import sqlite3
import datetime


class ManageFollow:
    def __init__(self, user, api):
        """
        ManageFollow object keeps track of user and tweets in an sqlite table

        :param user tweepy.API.me() : Current user object for tweepy bot
        :param api tweepy.API: api object from tweepy library
        """
        self.user = user
        self.api = api

    def update_table(self, follower):
        """
        Add Follower entry to User table.

        :param follower string: Follower Name/ID to be recorded in database.
        """
        connection = sqlite3.connect('data.db')
        c = connection.cursor()
        c.execute('''SELECT * FROM {tab} WHERE compte = ?;'''.format(tab=self.user.screen_name), (str(follower),))
        data = c.fetchall()

        # If this id exist
        if len(data) == 0:
            c.execute('''INSERT INTO {tab}(compte,date) VALUES (:compte, :date);'''.format(
                tab=self.user.screen_name), (follower, datetime.datetime.now()))
        else:
            c.execute('''UPDATE {tab} SET date = ? WHERE compte = ?'''.format(
                tab=self.user.screen_name), (datetime.datetime.now(), str(follower),))
        c.close()
        connection.commit()

    def unfollow(self):
        """
        Remove past users with follow date > 2 months.

        """
        print("We check if there are accounts to unfollow ...")
        connection = sqlite3.connect('data.db')
        c = connection.cursor()
        c.execute("""SELECT * FROM {tab};""".format(tab=self.user.screen_name))
        data = c.fetchall()
        unfollow_count = 0
        for i in data:
            try:
                date = datetime.datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S.%f")

                # Add 2 Months into Next Year
                newyear = date.year + 1 if date.month > 10 else date.year
                newmonth = (date.month + 2) % 12
                date = date.replace(month=newmonth, year=newyear)

                if datetime.datetime.now() > date:
                    c.execute('''DELETE FROM {tab} WHERE compte = ?;'''.format(tab=self.user.screen_name), (str(i[1]),))
                    self.api.destroy_friendship(i[1])
                    unfollow_count += 1

            except Exception:
                pass

        print("unfollow accounts : ", str(unfollow_count))
        c.close()
        connection.commit()


def create_tables(user):
    """
    Create new tables for each user.

    :param user string: Name of new user to create.
    """
    connection = sqlite3.connect('data.db')
    c = connection.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS {tab}
        (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, compte text, date DATE);'''.format(tab=user.screen_name))
    c.close()
    connection.commit()
