# Standard libraries
import logging
import random
import time

# Third Party Libraries
import tweepy


class BypassAntiBot:
    def __init__(self, api):
        """
        BypassAntiBot constructor containing anti bot avoidance logic

        :param api tweepy.API: api object for current tweepy user
        """
        self.api = api

    def bypass(self):
        """
        Randomly Retweet 5 tweets & Randomly Tweet 10 things.
        """
        try:
            logging.info("Bypass anti-bot protections ...")
            self.randomretweet(5)
            self.randomtweet(10)
            logging.info("Anti-bot bypass completed !")

        except tweepy.TweepError as e:
            if e.api_code == 326:
                pass

    def remaining_retweet_calculation(self):
        """ Check for number of ReTweets needed to bypass  """
        retweet_count = 0
        for tweet in self.api.user_timeline(count=200, tweet_mode="extended"):
            if tweet.retweeted:
                retweet_count += 1
        remaining_retweet = round(-(40 - retweet_count/2) / (1/2))
        return remaining_retweet

    def remaining_retweetfollow_calculation(self):
        """ Check for number of ReTweet Follow needed to bypass """
        follow_count, retweet_count = 0, 0
        for tweet in self.api.user_timeline(count=200, tweet_mode="extended"):
            if tweet.retweeted:
                retweet_count += 1
                if "FOLLOW" in tweet.full_text.upper():
                    follow_count += 1

        remaining_tweet = (follow_count * 100) / retweet_count
        return remaining_tweet

    def randomretweet(self, retweet_count):
        """
        Randomly select trending tweets and Retweet them.

        :param retweet_count int: number of trending tweets to retweet.
        """

        # Get tweet at Trending place 610264,
        trend_api_response = self.api.trends_place(610264)
        # Pick Names of Trending Topics
        trends = list([trend['name'] for trend in trend_api_response[0]['trends']])
        # Randomly Select Tweet number in trending topic
        random_count = random.randrange(0, len(trends))
        # Follow remaining retweet count for logging
        remaining_retweet = retweet_count

        for tweet in tweepy.Cursor(self.api.search,
                                   q=trends[random_count],
                                   result_type="recent",
                                   lang="fr").items(retweet_count):
            try:
                tweet.retweet()

                next_retweet_sleep_count = random.randrange(10, 20)
                remaining_retweet -= 1

                logging.info("Random retweet done, %s remaining, sleeping for %ss...",
                             str(remaining_retweet),
                             str(next_retweet_sleep_count))

                time.sleep(next_retweet_sleep_count)  # Randomly stop activity for 10-20 seconds

            except tweepy.TweepError as e:
                if e.api_code == 185:
                    logging.warning("Message en attente, on a envoyé trop de message")
                    time.sleep(1500)
                    # TODO - Transformer le sleep en pass pour passer au compte d'après sans bloquer ?
                elif (e.api_code == 327) or (e.api_code == 326):
                    pass
                else:
                    logging.error(e.reason)
            except StopIteration:
                break

    def randomtweet(self, tweet_count):
        """
        Randomly Tweet thing.

        :param tweet_count int: Number of tweets to send.
        """
        try:
            # Get Tweets
            trends_api_response = self.api.trends_place(610264)
            trends = list([trend['name'] for trend in trends_api_response[0]['trends']])
            random_count = random.randrange(0, len(trends))

            # Follow remaining retweet count for logging
            remaining_tweet = tweet_count

            for tweet in tweepy.Cursor(self.api.search,
                                       q=trends[random_count] + " -filter:replies -filter:media -filter:retweets",
                                       lang="fr", tweet_mode="extended", result_type='recent').items(tweet_count):

                full_text = tweet.retweeted_status.full_text if hasattr(tweet, 'retweeted_status') else tweet.full_text

                if 'CONCOURS' not in full_text.upper():

                    # We don't want to notify other people
                    if "@" in full_text:
                        full_text = full_text.replace("@", " ")

                    # We remove hashtags to be discreet.
                    if "#" in full_text:
                        full_text = full_text.replace("#", " ")

                    self.api.update_status(full_text)

                next_tweet_sleep_count = random.randrange(10, 20)
                remaining_tweet -= 1

                logging.info("Random tweet done, %s remaining, sleeping for %ss...",
                             str(remaining_tweet),
                             str(next_tweet_sleep_count))

                time.sleep(next_tweet_sleep_count)

        except tweepy.TweepError as e:
            if e.api_code == 185:
                logging.warning("Message en attente, on a envoyé trop de message")
                time.sleep(1500)
            elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186) or (e.api_code == 326):
                pass
            else:
                logging.error(e.reason)
