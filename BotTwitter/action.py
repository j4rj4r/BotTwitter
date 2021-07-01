# Standard libraries
import logging
import random
import re
import time
from datetime import datetime, timedelta

# third party libraries
import tweepy


class Action:
    def __init__(self, api, user, configuration):
        """
        Tweet class constructor, requires api object and user object

        :param api: api object from tweepy library
        :param user: User object for current bot
        :param configuration : configuration dictionary
        """
        self.user = user
        self.api = api
        self.configuration = configuration

    def search_tweets(self):
        """
        Search for tweets and return a list of tweets based on the configuration.
        """
        action = []
        regex_detect_tag = [r"\b(\w*INVIT(E|É)\w*)\b",
                            r"\b(\w*IDENTIFI(E|É)\w*)\b",
                            r"\b(\w*TAG\w*)\b",
                            r"\b(\w*MENTIONN(E|É)\w*)\b"]
        regex_detect_tag = re.compile('|'.join(regex_detect_tag), re.IGNORECASE)

        for word in self.configuration['words_to_search']:
            logging.info('Searching tweet with the word : %s', word)
            for tweet in tweepy.Cursor(self.api.search,
                                       q=word, since=(
                            datetime.now() - timedelta(self.configuration['nb_days_rollback'])).strftime('%Y-%m-%d'),
                                       lang="fr", tweet_mode="extended").items(self.configuration['max_retrieve']):

                if tweet.retweet_count > self.configuration['min_retweet']:
                    is_in_blacklist = [ele for ele in self.configuration['words_to_blacklist'] if
                                       (ele in tweet.full_text.upper())]
                    if not is_in_blacklist:
                        # Check if it's a retweet
                        if hasattr(tweet, 'retweeted_status'):
                            screen_name = tweet.retweeted_status.author.screen_name
                            entities = tweet.retweeted_status.entities
                            full_text = tweet.retweeted_status.full_text
                        else:
                            screen_name = tweet.user.screen_name
                            entities = tweet.entities
                            full_text = tweet.full_text

                        # Check if Tweet Author is blacklisted or not
                        if screen_name not in self.configuration['accounts_to_blacklist']:

                            # Check for INVITE/TAG/MENTIONNE in retweet text
                            if re.search(regex_detect_tag, full_text):

                                # if comment with hashtag is enabled
                                if self.configuration['comment_with_hashtag']:
                                    # If there are hashtags in the tweet
                                    if len(entities['hashtags']) > 0:
                                        # Clean Hastags
                                        h_list = self.manage_hashtag(entities['hashtags'],
                                                                     self.configuration['hashtag_to_blacklist'])
                                        # If we find Hashtags -> Record the tweet
                                        if h_list:
                                            dict_action = {'tweet_object': tweet, 'hashtag': 1, 'tag': 1}
                                            action.append(dict_action)
                                        else:
                                            dict_action = {"tweet_object": tweet, "hashtag": 0, 'tag': 1}
                                            action.append(dict_action)
                                    else:
                                        dict_action = {"tweet_object": tweet, "hashtag": 0, 'tag': 1}
                                        action.append(dict_action)
                                else:
                                    dict_action = {"tweet_object": tweet, "hashtag": 0, 'tag': 1}
                                    action.append(dict_action)

                            # If regex-tags not found
                            else:
                                # if comment with hashtag is enabled
                                if self.configuration['comment_with_hashtag']:
                                    # If there are hashtags in the tweet
                                    if len(entities['hashtags']) > 0:
                                        # Clean Hastags
                                        h_list = self.manage_hashtag(entities['hashtags'],
                                                                     self.configuration['hashtag_to_blacklist'])
                                        # If we find Hashtags
                                        if h_list:
                                            dict_action = {'tweet_object': tweet, 'hashtag': 1, 'tag': 0}
                                            action.append(dict_action)
                                        else:
                                            dict_action = {'tweet_object': tweet, 'hashtag': 0, 'tag': 0}
                                            action.append(dict_action)
                                    else:
                                        dict_action = {'tweet_object': tweet, 'hashtag': 0, 'tag': 0}
                                        action.append(dict_action)
                                else:
                                    dict_action = {'tweet_object': tweet, 'hashtag': 0, 'tag': 0}
                                    action.append(dict_action)

        return action

#To Do
    def manage_action(self, list_action, sentence_for_tag, list_name, hashtag_to_blacklist, managefollow,
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
        for action in list_action:
            tweet = action['tweet_object']

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
