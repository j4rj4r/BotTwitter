# Standard libraries
import datetime
import re
import logging

import BotTwitter.constants as const
import BotTwitter.database_client as database_client

class Manage_Giveaway:
    def __init__(self, user):
        """
        GestionGiveaway constructor
        """
        self.user = user
        self.database_path = const.DB_FILE
        self.database = database_client.database(self.database_path)
        self.database_giveaway = self.database.Giveaways()

    def add_giveaway(self, GiveawayUserId=None, GiveawayUsername=None, TweetId=None, TweetMessage=None, NeedTags=None, NeedRt=None, 
                NeedComment=None, NeedLike=None, NeedFollow=None,  DateBot=datetime.datetime.now(), TagsBot=None, RtBot=None, LikeBot=None, CommentBot=None,
                FollowBot=None, PrivateMessage=False):
        """
        Add a giveaway record to the database

        :param UserId Integer/Boolean : User account id
        :param GiveawayUserId Integer/Boolean : User account id of the creator of the giveaway
        :param GiveawayUsername String : User account name of the creator of the giveaway
        :param TweetId Integer/Boolean : Tweet/Giveaway id
        :param TweetMessage String : Tweet/Giveaway message text
        :param NeedTags Integer/Boolean : Giveaway ask for Tags other users
        :param NeedRt Integer/Boolean : Giveaway ask for RT action
        :param NeedComment Integer/Boolean : Giveaway ask for Comment
        :param NeedLike Integer/Boolean : Giveaway ask for Like
        :param NeedFollow Integer/Boolean :  Giveaway ask for Follows
        :param DateBot Integer/Boolean : Date of participation to the giveaway
        :param TagsBot Integer/Boolean : Bot have tags users on this giveaway
        :param RtBot Integer/Boolean : Bot have RT this giveaway
        :param FollowBot Integer/Boolean : Bot have Follow the author of this giveaway
        :param LikeBot Integer/Boolean : Bot have Like this giveaway
        :param CommentBot Integer/Boolean : Bot have comment users on this giveaway
        :param PrivateMessage Integer/Boolean : Bot user have been contact  by the author of the giveaway after participation
        """

        #NeedRt='', NeedLike='', NeedFollow='',
        # Detect if the tweet require actions

        regex_detect_tag = re.compile('|'.join(const.regex_detect_tag), re.IGNORECASE)
        regex_detect_like = re.compile('|'.join(const.regex_detect_like), re.IGNORECASE)
        regex_detect_rt = re.compile('|'.join(const.regex_detect_rt), re.IGNORECASE)
        regex_detect_comment = re.compile('|'.join(const.regex_detect_comment), re.IGNORECASE)
        regex_detect_follow = re.compile('|'.join(const.regex_detect_follow), re.IGNORECASE)

        tweet_text = TweetMessage
        is_present_keyword_tag = re.search(regex_detect_tag, tweet_text) is not None
        is_present_keyword_like = re.search(regex_detect_like, tweet_text) is not None
        is_present_keyword_rt = re.search(regex_detect_rt, tweet_text) is not None
        is_present_keyword_comment = re.search(regex_detect_comment, tweet_text) is not None
        is_present_keyword_follow = re.search(regex_detect_follow, tweet_text) is not None
        # set variable if None
        NeedTags = (NeedTags or is_present_keyword_tag or False)
        NeedLike = (NeedLike or is_present_keyword_like or False)
        NeedRt = (NeedRt or is_present_keyword_rt or False)
        NeedComment = (NeedComment or is_present_keyword_comment or False)
        NeedFollow = (NeedFollow or is_present_keyword_follow or False)

        # Insert in database
        self.database_giveaway.add_giveaway(
                UserId      = self.user.id,
                GiveawayUserId = GiveawayUserId,
                GiveawayUsername = GiveawayUsername,
                TweetId     = TweetId,
                TweetMessage = TweetMessage,
                NeedTags    = NeedTags,
                NeedRt      = NeedRt,
                NeedComment = NeedComment,
                NeedLike    = NeedLike,
                NeedFollow  = NeedFollow,
                DateBot     = DateBot,
                TagsBot     = TagsBot,
                RtBot       = RtBot,
                FollowBot   = FollowBot,
                LikeBot     = LikeBot,
                CommentBot  = CommentBot,
                PrivateMessage = PrivateMessage
        )

    def win(self, authorId :int):
        """
        Set a giveaway to won and return associate data

        :param authorId int: Author
        
        :return TweetId, GiveawayUsername, DateBot, TweetMessage
        """
        giveaway_rows = self.database_giveaway.get_giveaways(UserId=self.user.id, GiveawayUserId=authorId)
        if len(giveaway_rows) > 0:
            # update giveway as won
            giveaway_row = giveaway_rows[0]
            logging.info('Update database to save we probably won the giveaway '+ str(giveaway_row.GiveawayId) +' from tweet '+ str(giveaway_row.TweetId)
                            +' posted by @'+giveaway_row.GiveawayUsername)
            self.database_giveaway.update_giveaway(GiveawayId=giveaway_row.GiveawayId, new_PrivateMessage=True)
            return giveaway_row.TweetId, giveaway_row.GiveawayUsername, giveaway_row.DateBot, giveaway_row.TweetMessage