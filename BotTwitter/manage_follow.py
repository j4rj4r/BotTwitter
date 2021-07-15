# Standard libraries
import datetime
import logging


import BotTwitter.constants as const
import BotTwitter.database_client as database_client


class Manage_follow:
    def __init__(self, user, api):
        """
        ManageFollow object keeps track of user and tweets in an sqlite table

        :param user tweepy.API.me() : Current user object for tweepy bot
        :param api tweepy.API: api object from tweepy library
        """
        self.user = user
        self.api = api
        self.database_path = const.DB_FILE
        self.database = database_client.database(self.database_path)
        self.database_follows = self.database.Follows()


    def update_table(self, follower):
        """
        Add Follower entry to User table.

        :param follower string: Follower Name/ID to be recorded in database.
        """
        follows_rows = self.database_follows.get_follows(UserId=str(self.user.id), FollowIdAccount=str(follower))
        if len(follows_rows) > 0:
            # already follow, update the date with the current date
            self.database_follows.update_follow(FollowId=follows_rows[0].FollowId, 
                                                new_UserId=str(self.user.id), 
                                                new_DateFollow=datetime.datetime.now())
        else:
            # Insert new line in follows table with the current date
            self.database_follows.add_follow(str(self.user.id), str(follower), datetime.datetime.now())


    def unfollow(self):
        """
        Remove past users with follow date > 2 months.

        """
        logging.info("We check if there are accounts to unfollow ...")
        follows_rows = self.database_follows.get_follows(UserId=str(self.user.id))
        unfollow_count = 0
        for follows_row in follows_rows:
            try:
                date = datetime.datetime.strptime(follows_row.DateFollow, "%Y-%m-%d %H:%M:%S.%f")

                # Add 2 Months into Next Year
                newyear = date.year + 1 if date.month > 10 else date.year
                newmonth = (date.month + 2) % 12
                date = date.replace(month=newmonth, year=newyear)

                if datetime.datetime.now() > date:
                    # Delete row in database
                    self.database_follows.delete_follow(FollowId=follows_row.FollowId)
                    # Unfollow 
                    self.api.destroy_friendship(follows_row.FollowIdAccount)
                    unfollow_count += 1

            except Exception as e:
                logging.error('Error occurred during unfollow :')
                logging.error(e)
                pass

        logging.info("Unfollow accounts : %s", str(unfollow_count))