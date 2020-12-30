# Standard libraries
import logging
import random
import time

# Third Party Libraries
import tweepy
import feedparser


class BypassAntiBot:
    def __init__(self, api, flux_rss, user):
        """
        BypassAntiBot constructor containing anti bot avoidance logic

        :param api tweepy.API: api object for current tweepy user
        """
        self.api = api
        self.flux_rss = flux_rss
        self.user = user

    def bypass(self):
        """
        Randomly Retweet 5 tweets & Randomly Tweet 10 things.
        """
        try:
            logging.info("Bypass anti-bot protections ...")
            self.randomretweet()
            quit()
            self.rss_and_tweet()
            logging.info("Anti-bot bypass completed !")

        except tweepy.TweepError as e:
            if e.api_code == 326:
                pass

    def random_retweet_calculation(self):
        """ Check for number of ReTweet Follow needed to bypass """
        follow_count, retweet_count = 0, 0
        for tweet in self.api.user_timeline(count=200, tweet_mode="extended"):
            if tweet.retweeted:
                retweet_count += 1
                if "FOLLOW" in tweet.full_text.upper():
                    follow_count += 1
        percent_RtFol = (follow_count * 100) / retweet_count
        if percent_RtFol > 25:
            randomrt = ( follow_count * 4 ) - retweet_count
            logging.info("Il y a " + str(percent_RtFol) + " % de RT pour les concours on va faire " + str(randomrt) + " RT random")
            if randomrt > 15:
                randomrt =  15
                logging.info("On va tweets uniquement " + str(randomrt) + " pour l'instant")
        else:
            logging.info("Il y a " + str(percent_RtFol) + " % de RT pour les concours on passe a la suite")
            randomrt = 0
        return randomrt

    def random_tweet_calculation(self):
        retweet_count = 0
        for tweet in self.api.user_timeline(count=200, tweet_mode="extended"):
            if tweet.retweeted:
                retweet_count += 1
        if retweet_count > 100:
            randomtweet =  retweet_count - 100
            logging.info("actuellement il y a " + str(retweet_count) + " retweets pour 200 tweets il faut faire " + str(randomtweet) + "tweets random")
            if randomtweet > 15:
                randomtweet =  15
                logging.info("On va tweets uniquement " + str(randomtweet) + " pour l'instant")
        else:
            logging.info("Il y a moins de 50% de ReTweets sur le compte on passe a la suite")
            randomtweet =  0
        return randomtweet

    def randomretweet(self):
        """
        Randomly select trending tweets and Retweet them.

        :param remaining_retweet int: number of trending tweets to retweet.
        """
        nbtweet = self.random_retweet_calculation()
        logging.info("Random retweet started, %s remaining",
                    str(nbtweet))
        time.sleep(5)
        if nbtweet > 0:
            # Get tweet at Trending place 610264,
            trend_api_response = self.api.trends_place(610264)
            # Pick Names of Trending Topics
            trends = list([trend['name'] for trend in trend_api_response[0]['trends']])
            # Randomly Select Tweet number in trending topic
            random_count = random.randrange(0, len(trends))
            for tweet in tweepy.Cursor(self.api.search,
                                    q=trends[random_count],
                                    result_type="recent",
                                    include_entities="True",
                                    lang="fr").items(nbtweet):
                try:
                    tweet.retweet()
                    next_retweet_sleep_count = random.randrange(10, 20)
                    nbtweet -= 1
                    logging.info("Random retweet done, %s remaining, sleeping for %ss...",
                                str(nbtweet),
                                str(next_retweet_sleep_count))
                    time.sleep(next_retweet_sleep_count)  # Randomly stop activity for 10-20 seconds
                except tweepy.TweepError as e:
                    if e.api_code == 185:
                        logging.info("Message en attente, on a envoyé trop de message")
                        time.sleep(1500)
                    elif (e.api_code == 327) or (e.api_code == 326):
                        pass
                    else:
                        logging.info(e.reason)
                except StopIteration:
                    break

    def rss_and_tweet(self):
            nbtweet = self.random_tweet_calculation()
            rsslog = str(self.user.screen_name) + "_rsslog.log"
            with open(rsslog) as f:
                lines = f.readlines()
            feeds = [] # list of feed objects
            for url in self.flux_rss:
                feeds.append(feedparser.parse(url))
            for feed in feeds:
                for post in feed.entries:
                    if nbtweet > 0:
                        if (post.link + "\n" or post.link) in lines:
                            pass
                        else:
                            try:
                                mode_message = random.randrange(1, 3)
                                if mode_message == 1:
                                    message = post.title
                                else:
                                    message = post.title + " " + post.link
                                with open(rsslog, "a") as f:
                                    f.write(post.link + "\n")
                                logging.info(post.title)
                                self.api.update_status(message)
                                next_tweet_sleep_count = random.randrange(10, 20)
                                nbtweet -= 1
                                logging.info("Random tweet done, %s remaining, sleeping for %ss...",
                                                                                str(nbtweet),
                                                                                str(next_tweet_sleep_count))
                                time.sleep(next_tweet_sleep_count)
                            except tweepy.TweepError as e:
                                if e.api_code == 185:
                                    logging.info("Message en attente, on a envoyé trop de message")
                                    time.sleep(1500)
                                elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186) or (e.api_code == 326):
                                    pass
                                else:
                                    logging.info(e.reason)
