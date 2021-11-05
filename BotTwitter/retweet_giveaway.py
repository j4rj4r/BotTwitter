# Standard libraries
import logging
import random
import re
import time
from datetime import datetime, timedelta

# third party libraries
import tweepy


class RetweetGiveaway:
    def __init__(self, api, user):
        """
        RetweetGiveaway class constructor, requires api object and user object

        :param api tweepy.API: api object from tweepy library
        :param user tweepy.API.verify_credentials() : User object for current bot
        """
        self.user = user
        self.api = api
        self.bot_action = []

    def check_retweet(self, words_to_search, accounts_to_blacklist, hashtag_to_blacklist, giveaway_to_blacklist,
                      comment_with_hashtag, max_giveaway, nb_days_rollback):
        """
        Check for useful tweets by filtering out blacklisted

        :param words_to_search list: List of Keywords to Search tweet for
        :param accounts_to_blacklist list: List of Blacklisted Accounts to Ignore
        :param hashtag_to_blacklist list: List of Blacklisted Hashtags in tweets to ignore
        :param giveaway_to_blacklist list: List of Blacklisted Giveaways to Ignore
        :param comment_with_hashtag boolean: If we comment with hashtag
        :param max_giveaway integer: Maximum number of giveaway retrieve for each word
        :param nb_days_rollback integer: Number of day back
        """
        action = []
        regex_detect_tag = [r"\b(\w*INVIT(E|É)\w*)\b",
                            r"\b(\w*IDENTIFI(E|É)\w*)\b",
                            r"\b(\w*TAG\w*)\b",
                            r"\b(\w*MENTIONN(E|É)\w*)\b"]
        regex_detect_tag = re.compile('|'.join(regex_detect_tag), re.IGNORECASE)

        for word in words_to_search:

            logging.info("Searching giveaway with the word : %s", word)
            for tweet in tweepy.Cursor(self.api.search,
                                       q=word, since=(datetime.now() - timedelta(nb_days_rollback)).strftime('%Y-%m-%d'),
                                       lang="fr", tweet_mode="extended").items(max_giveaway):

                if tweet.retweet_count > 5:
                    is_in_blacklist = [ele for ele in giveaway_to_blacklist if (ele in tweet.full_text.upper())]
                    if is_in_blacklist:
                        pass
                    else:
                        # Check if it's a retweet
                        if hasattr(tweet, 'retweeted_status'):
                            screen_name = tweet.retweeted_status.author.screen_name
                            entities = tweet.retweeted_status.entities
                            full_text = tweet.retweeted_status.full_text
                            extra = 0
                        else:
                            screen_name = tweet.user.screen_name
                            entities = tweet.entities
                            full_text = tweet.full_text
                            extra = 3

                        # Check if Tweet Author is blacklisted or not
                        if screen_name not in accounts_to_blacklist:

                            # Check for INVITE/TAG/MENTIONNE in retweet text
                            if re.search(regex_detect_tag, full_text):

                                # Check if tweet has Hashtags
                                if len(entities['hashtags']) > 0:
                                    # if comment with hashtag is enabled
                                    if comment_with_hashtag:
                                        # Clean Hastags
                                        h_list = self.manage_hashtag(entities['hashtags'],
                                                                     hashtag_to_blacklist)
                                        # If we find Hashtags -> Record the tweet
                                        if h_list:
                                            action.append(tweet)
                                            action.append(1 + extra)
                                            self.bot_action.append(action)
                                        else:
                                            action.append(tweet)
                                            action.append(2 + extra)
                                            self.bot_action.append(action)
                                    else:
                                        action.append(tweet)
                                        action.append(2 + extra)
                                        self.bot_action.append(action)
                                # Else Select Action 2
                                else:
                                    action.append(tweet)
                                    action.append(2 + extra)
                                    self.bot_action.append(action)

                            # If regex-tags not found, record the tweet without action number
                            else:
                                action.append(tweet)
                                self.bot_action.append(action)

                        action = []

        return self.bot_action

    def manage_giveaway(self, list_giveaway, sentence_for_tag, list_name, hashtag_to_blacklist, managefollow,
                        like_giveaway, nb_account_to_tag):
        """
        Handle Give away tweets by following/commenting/tagging depending on the giveaway levels

        :param list_giveaway list: List of Giveaways tweets and (optional) Giveaway levels
        :param sentence_for_tag list: List of Random Sentences to use for commenting
        :param list_name list: List of Names to Randomly Tag on giveaways
        :param hashtag_to_blacklist list: List of hastags to blacklist
        :param managefollow managefollow: Database management object from ManageFollow
        :param like_giveaway boolean: If we like giveaway
        """
        for giveaway in list_giveaway:
            tweet = giveaway[0]

            try:
                if hasattr(tweet, 'retweeted_status'):
                    retweeted = tweet.retweeted_status.retweeted
                    id_ = tweet.retweeted_status.id
                    author_id = tweet.retweeted_status.author.id
                    entities = tweet.retweeted_status.entities
                    screen_name = tweet.retweeted_status.user.screen_name
                else:
                    retweeted = tweet.retweeted
                    id_ = tweet.id
                    author_id = tweet.user.id
                    entities = tweet.entities
                    screen_name = tweet.user.screen_name

                if not retweeted:
                    self.api.retweet(id_)
                    if like_giveaway:
                        self.api.create_favorite(id_)

                    self.api.create_friendship(author_id)

                    if len(giveaway) == 2:
                        comment_level = giveaway[1]
                        self.comment(tweet, sentence_for_tag, comment_level, list_name, hashtag_to_blacklist,
                                     nb_account_to_tag)

                    managefollow.update_table(author_id)

                    if len(entities['user_mentions']) > 0:
                        for mention in entities['user_mentions']:
                            self.api.create_friendship(mention['id'])
                            managefollow.update_table(mention['id'])

                    random_sleep_time = random.randrange(10, 20)
                    logging.info("You participated in the giveaway of : @%s. Sleeping for %ss...",
                                 screen_name,
                                 str(random_sleep_time))

                    time.sleep(random_sleep_time)

            except tweepy.TweepError as e:
                if e.api_code == 327:
                    pass
                elif e.api_code == 161:
                    logging.warning("The account can no longer follow. We go to the next step.")
                    break
                elif e.api_code == 136:
                    logging.info("You have been blocked by: %s", screen_name)
                    break
                elif e.api_code == 326:
                    logging.warning("You have to do a captcha on the account: %s", self.user.screen_name)
                    break
                else:
                    logging.error(e)

    def comment(self, tweet, sentence_for_tag, hashtag, list_name, hashtag_to_blacklist, nb_account_to_tag):
        """
        Add Comment to a given tweet using some rules.

        :param tweet tweepy.tweet: Tweet object  from tweepy library
        :param sentence_for_tag list: List of random sentences
        :param hashtag list: List of Hashtags
        :param list_name list: List of user names
        :param hashtag_to_blacklist list: List of Blacklisted Hastags to avoid
        """
        random.shuffle(list_name)
        nbrandom = random.randrange(0, len(sentence_for_tag))
        randomsentence = sentence_for_tag[nbrandom]

        # Random Sentence + Tag Comment + Hashtag Comment + Update Status
        if hashtag == 1:
            comment = "@" + tweet.retweeted_status.author.screen_name + " " + randomsentence + " "
            comment = self.add_tag_comment(list_name, comment, nb_account_to_tag)
            comment = self.add_hashtag_comment(comment, tweet.retweeted_status.entities['hashtags'],
                                               hashtag_to_blacklist)
            self.api.update_status(comment, tweet.retweeted_status.id)

        # Random Sentence + Tag Comment + Update Status
        elif hashtag == 2:
            comment = "@" + tweet.retweeted_status.author.screen_name + " " + randomsentence + " "
            comment = self.add_tag_comment(list_name, comment, nb_account_to_tag)
            self.api.update_status(comment, tweet.retweeted_status.id)

        # Hashtag Comment + Update Status
        elif hashtag == 3:
            comment = "@" + tweet.retweeted_status.author.screen_name + " "
            comment = self.add_hashtag_comment(comment, tweet.retweeted_status.entities['hashtags'],
                                               hashtag_to_blacklist)
            self.api.update_status(comment, tweet.retweeted_status.id)

        # User - Random Sentence + Tag Comment + Hashtag Comment + Update Status
        elif hashtag == 4:
            comment = "@" + tweet.user.screen_name + " " + randomsentence + " "
            comment = self.add_tag_comment(list_name, comment, nb_account_to_tag)
            comment = self.add_hashtag_comment(comment, tweet.entities['hashtags'],
                                               hashtag_to_blacklist)
            self.api.update_status(comment, tweet.id)

        # User - Random Sentence + Tag Comment + Update Status
        elif hashtag == 5:
            comment = "@" + tweet.user.screen_name + " " + randomsentence + " "
            comment = self.add_tag_comment(list_name, comment, nb_account_to_tag)
            self.api.update_status(comment, tweet.id)

        # User - Hashtag Comment + Update Status
        elif hashtag == 6:
            comment = "@" + tweet.user.screen_name + " "
            comment = self.add_hashtag_comment(comment, tweet.entities['hashtags'],
                                               hashtag_to_blacklist)
            self.api.update_status(comment, tweet.id)

    def manage_hashtag(self, hashtag_list, hashtag_to_blacklist):
        """
        Filter Blacklisted Hastags

        :param hashtag_list list: List of Hashtags from Tweet
        :param hashtag_to_blacklist list: List of BlackListed Hashtags
        """
        h_list = []
        for h in hashtag_list:
            h_list.append(h['text'].upper())

        return list(set(h_list) - set(hashtag_to_blacklist))

    def add_tag_comment(self, list_name, comment, nb_account_to_tag):
        """
        Tag other users in comment.

        :param list_name list: List of user names to add to comment
        :param comment string: Tweet/text/Comment
        """
        nbusernotif = 0
        for username in list_name:
            if nbusernotif < nb_account_to_tag:
                # We don't want to tag ourselves
                if username == "@" + self.user.screen_name:
                    pass
                else:
                    comment = comment + username + " "
                    nbusernotif += 1
        return comment

    def add_hashtag_comment(self, comment, hashtag_list, hashtag_to_blacklist):
        """
        Add hashtag in Comments

        :param comment string: Comment to which to add hashtags
        :param hashtag_list list: List of Hashtags
        :param hashtag_to_blacklist list: List of Blacklisted Hashtags to avoid
        """
        h_list = self.manage_hashtag(hashtag_list, hashtag_to_blacklist)
        for hashtag in h_list:
            comment = comment + "#" + hashtag + " "
        return comment
