# Standard libraries
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
            print("Bypass anti-bot protections ...")
            self.randomretweet(5)
            self.randomtweet(10)
            print("Anti-bot bypass completed !")

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

    def randomretweet(self, remaining_retweet):
        """
        Randomly select trending tweets and Retweet them.

        :param remaining_retweet int: number of trending tweets to retweet.
        """

        # Get tweet at Trending place 610264,
        trend_api_response = self.api.trends_place(610264)
        # Pick Names of Trending Topics
        trends = list([trend['name'] for trend in trend_api_response[0]['trends']])
        # Randomly Select Tweet number in trending topic
        random_count = random.randrange(0, len(trends))

        for tweet in tweepy.Cursor(self.api.search,
                                   q=trends[random_count],
                                   result_type="recent",
                                   lang="fr").items(remaining_retweet):
            try:
                tweet.retweet()
                time.sleep(random.randrange(10, 20))  # Randomly stop activity for 10-20 seconds

            except tweepy.TweepError as e:
                if e.api_code == 185:
                    print("Message en attente, on a envoyé trop de message")
                    time.sleep(1500)
                elif (e.api_code == 327) or (e.api_code == 326):
                    pass
                else:
                    print(e.reason)
            except StopIteration:
                break

    def randomtweet(self, remaining_tweet):
        """
        Randomly Tweet thing.

        :param remaining_tweet int: Number of tweets to send.
        """
        try:
            # Get Tweets
            trends_api_response = self.api.trends_place(610264)
            trends = list([trend['name'] for trend in trends_api_response[0]['trends']])
            random_count = random.randrange(0, len(trends))

            for tweet in tweepy.Cursor(self.api.search,
                                       q=trends[random_count] + " -filter:replies -filter:media -filter:retweets",
                                       lang="fr", tweet_mode="extended", result_type='recent').items(remaining_tweet):

                full_text = tweet.retweeted_status.full_text if hasattr(tweet, 'retweeted_status') else tweet.full_text

                if 'CONCOURS' not in full_text.upper():

                    # We don't want to notify other people
                    if "@" in full_text:
                        full_text = full_text.replace("@", " ")

                    # We remove hashtags to be discreet.
                    if "#" in full_text:
                        full_text = full_text.replace("#", " ")

                    self.api.update_status(full_text)

                time.sleep(random.randrange(10, 20))

        except tweepy.TweepError as e:
            if e.api_code == 185:
                print("Message en attente, on a envoyé trop de message")
                time.sleep(1500)
            elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186) or (e.api_code == 326):
                pass
            else:
                print(e.reason)
