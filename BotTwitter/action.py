# Standard libraries
import logging
import random
import re
import time
from datetime import datetime, timedelta

import BotTwitter.constants as const
from BotTwitter.manage_follow import Manage_follow
from BotTwitter.manage_giveaway import Manage_Giveaway

# third party libraries
import tweepy

class Action:
    def __init__(self, configuration, list_name, user, api):
        """
        Tweet class constructor, requires configuration dictionnary and username list

        :param configuration : configuration dictionary
        :param list_name : username list
        :param user : current user account
        :param api : api references
        """
        self.configuration = configuration
        self.list_name = list_name
        self.user = user
        self.api = api
        self.manage_follow = Manage_follow(user, api) # Init follow management
        self.manage_follow.unfollow() # Clear the follow list before to do any actions
        self.manage_giveaway = Manage_Giveaway(user) # Init giveaway management for stats

    def search_tweets(self, api):
        """
        Search for tweets and return a list of tweets based on the configuration.

        :param api : api object
        """
        action = []
        regex_detect_tag = re.compile('|'.join(const.regex_detect_tag), re.IGNORECASE)

        for word in self.configuration['words_to_search']:
            logging.info('Searching tweet with the word : %s', word)
            for tweet in tweepy.Cursor(api.search, q=word,
                                since=(datetime.now() - timedelta(self.configuration['nb_days_rollback'])).strftime('%Y-%m-%d'),
                                lang="fr", tweet_mode="extended").items(self.configuration['max_retrieve']):

                if tweet.retweet_count > self.configuration['min_retweet']:
                    # Blacklist words management 
                    blacklist = self.configuration['words_to_blacklist']
                    blacklist = [blacklist_elem.upper() for blacklist_elem in blacklist]
                    is_in_blacklist = False
                    for tweet_word_upper in tweet.full_text.upper().split():
                        if tweet_word_upper in blacklist:
                            is_in_blacklist = True

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
                            match_keyword_tag = re.search(regex_detect_tag, full_text)
                            is_present_keyword_tag = match_keyword_tag is not None
                            # if comment with hashtag is enabled
                            if self.configuration['comment_with_hashtag']:
                                # If there are hashtags in the tweet
                                if len(entities['hashtags']) > 0:
                                    # Clean Hastags
                                    h_list = self.manage_hashtag(entities['hashtags'])
                                    # If we find Hashtags -> Record the tweet
                                    if h_list:
                                        dict_action = {'tweet_object': tweet, 'hashtag': True, 'tag': is_present_keyword_tag}
                                        action.append(dict_action)
                                    else:
                                        dict_action = {"tweet_object": tweet, "hashtag": False, 'tag': is_present_keyword_tag}
                                        action.append(dict_action)
                                else:
                                    dict_action = {"tweet_object": tweet, "hashtag": False, 'tag': is_present_keyword_tag}
                                    action.append(dict_action)
                            else:
                                dict_action = {"tweet_object": tweet, "hashtag": False, 'tag': is_present_keyword_tag}
                                action.append(dict_action)
                    else:
                        logging.info("Blacklisted words match with the tweet : ", tweet.entities)
        return action


    def manage_action(self, list_action):
        """
        Handle Give away tweets by following/commenting/tagging depending on the giveaway levels

        :param list_action : List of Giveaways tweets and (optional) Giveaway levels
        """
        for action in list_action:
            tweet = action['tweet_object']

            action_rt, action_like, action_follow, action_tag = False, False, False, False
            need_tag = action["tag"]
            need_hashtag= action["hashtag"]

            try:
                if hasattr(tweet, 'retweeted_status'):
                    retweeted = tweet.retweeted_status.retweeted
                    favorited = tweet.retweeted_status.favorited
                    id_ = tweet.retweeted_status.id
                    author_id = tweet.retweeted_status.author.id
                    entities = tweet.retweeted_status.entities
                    screen_name = tweet.retweeted_status.user.screen_name
                    text = tweet.retweeted_status.full_text
                else:
                    retweeted = tweet.retweeted
                    favorited = tweet.liked
                    id_ = tweet.id
                    author_id = tweet.user.id
                    entities = tweet.entities
                    screen_name = tweet.user.screen_name
                    text = tweet.full_text

                if self.configuration['retweet_tweets']:
                    if not retweeted:
                        self.api.retweet(id_)
                        action_rt = True

                if self.configuration['like_tweets']:
                    if not favorited:
                        self.api.create_favorite(id_)
                        action_like = True

                if self.configuration['automatic_follow']:
                    self.api.create_friendship(author_id)
                    self.manage_follow.update_table(author_id)
                    action_follow = True

                if self.configuration['tag']:
                    self.comment(action)
                    action_tag = True

                if self.configuration['automatic_tag_follow'] :
                    if len(entities['user_mentions']) > 0:
                        for mention in entities['user_mentions']:
                            self.api.create_friendship(mention['id'])
                            self.manage_follow.update_table(mention['id'])

                    #Log participation and sleep a random time
                    self.manage_giveaway.add_giveaway(
                        GiveawayUserId=author_id, GiveawayUsername=screen_name, TweetId=id_, TweetMessage=text,
                        NeedTags=need_tag, DateBot=datetime.now(),
                        TagsBot=action_tag, RtBot=action_rt, FollowBot=action_follow, LikeBot=action_like, CommentBot=action_tag,
                        PrivateMessage=False
                    )
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
                    logging.error('Error occurred dunring action with the API:')
                    logging.error(e)

    def comment(self, action):
        """
        Add Comment to a given tweet using some rules.

        :param tweet tweepy.tweet: Tweet object  from tweepy library
        :param sentence_for_tag list: List of random sentences
        :param hashtag list: List of Hashtags
        :param list_name list: List of user names
        :param hashtag_to_blacklist list: List of Blacklisted Hastags to avoid
        """
        # Extract tweet and actions
        tweet = action["tweet_object"]
        hashtag = action["hashtag"]
        tag = action["tag"]
        need_comment = tag is not None

        sentence_for_tag = self.configuration["sentence_for_tag"]
        random.shuffle(self.list_name)
        nbrandom = random.randrange(0, len(sentence_for_tag))
        randomsentence = sentence_for_tag[nbrandom]

         # if the tweet ask for INVITE/TAG/MENTIONNE
        if need_comment is not None:
            # check context Tweet or retweet
            if tweet.retweeted_status is not None:
                # Context: Retweet
                # Random Sentence + Tag Comment + Hashtag Comment + Update Status
                if hashtag and tag:
                    comment = "@" + tweet.retweeted_status.author.screen_name + " " + randomsentence + " "
                    comment = self.add_tag_comment(self.list_name, comment)
                    comment = self.add_hashtag_comment(comment, tweet.retweeted_status.entities['hashtags'])
                    self.api.update_status(comment, tweet.retweeted_status.id)

                # Random Sentence + Tag Comment + Update Status
                elif not hashtag and tag:
                    comment = "@" + tweet.retweeted_status.author.screen_name + " " + randomsentence + " "
                    comment = self.add_tag_comment(self.list_name, comment)
                    self.api.update_status(comment, tweet.retweeted_status.id)

                # Hashtag Comment + Update Status
                elif hashtag and not tag:
                    comment = "@" + tweet.retweeted_status.author.screen_name + " "
                    comment = self.add_hashtag_comment(comment, tweet.retweeted_status.entities['hashtags'])
                    self.api.update_status(comment, tweet.retweeted_status.id)
            else:
                # Context: Tweet
                # User - Random Sentence + Tag Comment + Hashtag Comment + Update Status
                if hashtag and tag:
                    comment = "@" + tweet.user.screen_name + " " + randomsentence + " "
                    comment = self.add_tag_comment(self.list_name, comment)
                    comment = self.add_hashtag_comment(comment, tweet.entities['hashtags'])
                    self.api.update_status(comment, tweet.id)

                # User - Random Sentence + Tag Comment + Update Status
                elif not hashtag and tag:
                    comment = "@" + tweet.user.screen_name + " " + randomsentence + " "
                    comment = self.add_tag_comment(self.list_name, comment)
                    self.api.update_status(comment, tweet.id)

                # User - Hashtag Comment + Update Status
                elif hashtag and not tag:
                    comment = "@" + tweet.user.screen_name + " "
                    comment = self.add_hashtag_comment(comment, tweet.entities['hashtags'])
                    self.api.update_status(comment, tweet.id)

    def manage_hashtag(self, hashtag_list):
        """
        Filter Blacklisted Hastags

        :param hashtag_list list: List of Hashtags from Tweet
        :param hashtag_to_blacklist list: List of BlackListed Hashtags
        """
        hashtag_to_blacklist = [h_blacklisted_elem.upper() for h_blacklisted_elem in self.configuration["hashtag_to_blacklist"]] 
        h_list = []
        for h in hashtag_list:
            h_list.append(h['text'].upper())

        return list(set(h_list) - set(hashtag_to_blacklist))

    def add_tag_comment(self, list_name, comment):
        """
        Tag other users in comment.

        :param list_name list: List of user names to add to comment
        :param comment string: Tweet/text/Comment
        """
        nbusernotif = 0
        for username in self.list_name:
            if nbusernotif < self.configuration["nb_account_to_tag"]:
                # We don't want to tag ourselves
                if username == "@" + self.user.screen_name:
                    pass
                else:
                    comment = comment + username + " "
                    nbusernotif += 1
        return comment

    def add_hashtag_comment(self, comment, hashtag_list):
        """
        Add hashtag in Comments

        :param comment string: Comment to which to add hashtags
        :param hashtag_list list: List of Hashtags
        """
        h_list = self.manage_hashtag(hashtag_list)
        for hashtag in h_list:
            comment = comment + "#" + hashtag + " "
        return comment
