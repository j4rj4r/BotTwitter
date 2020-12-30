# Standard libraries
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
            print("Bypass anti-bot protections ...")
            self.randomretweet()
            self.rss_and_tweet()
            print("Anti-bot bypass completed !")

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
            print("Il y a " + str(percent_RtFol) + " % de RT pour les concours on va faire " + str(randomrt) + " RT random")
            if randomrt > 15:
                randomrt =  15
                print("On va tweets uniquement " + str(randomrt) + " pour l'instant")
        else:
            print("Il y a " + str(percent_RtFol) + " % de RT pour les concours on passe a la suite")
            randomrt = 0
        return randomrt

    def random_tweet_calculation(self):
        retweet_count = 0
        for tweet in self.api.user_timeline(count=200, tweet_mode="extended"):
            if tweet.retweeted:
                retweet_count += 1
        if retweet_count > 100:
            randomtweet =  retweet_count - 100
            print("actuellement il y a " + str(retweet_count) + " retweets pour 200 tweets il faut faire " + str(randomtweet) + "tweets random")
            if randomtweet > 15:
                randomtweet =  15
                print("On va tweets uniquement " + str(randomtweet) + " pour l'instant")
        else:
            print("Il y a moins de 50% de ReTweets sur le compte on passe a la suite")
            randomtweet =  0
        return randomtweet

    def randomretweet(self):
        """
        Randomly select trending tweets and Retweet them.

        :param remaining_retweet int: number of trending tweets to retweet.
        """
        nbtweet = self.random_retweet_calculation()
        if nbtweet > 0:
            # Get tweet at Trending place 610264,
            trend_api_response = self.api.trends_place(615702)
            # Pick Names of Trending Topics
            trends = list([trend['name'] for trend in trend_api_response[0]['trends']])
            # Randomly Select Tweet number in trending topic
            random_count = random.randrange(0, len(trends))

            for tweet in tweepy.Cursor(self.api.search,
                                    q=trends[random_count],
                                    result_type="popular",
                                    include_entities="True",
                                    lang="fr").items(randomrt):
                try:
                    tweet.retweet()
                    time.sleep(random.randrange(120, 180))  # Randomly stop activity for 10-20 seconds

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
                            print("Already print")
                        else:
                            try:
                                message = post.title + " " + post.link
                                print(post.title)
                                self.api.update_status(message)
                                nbtweet -= 1
                                with open(rsslog, "a") as f:
                                    f.write(post.link + "\n")
                                    time.sleep(random.randrange(120, 150))
                            except tweepy.TweepError as e:
                                if e.api_code == 185:
                                    print("Message en attente, on a envoyé trop de message")
                                    time.sleep(1500)
                                elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186) or (e.api_code == 326):
                                    pass
                                else:
                                    print(e.reason)

    def randomcopytweet(self, remaining_tweet):
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

                time.sleep(random.randrange(120, 180))

        except tweepy.TweepError as e:
            if e.api_code == 185:
                print("Message en attente, on a envoyé trop de message")
                time.sleep(1500)
            elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186) or (e.api_code == 326):
                pass
            else:
                print(e.reason)
