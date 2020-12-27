# Standard libraries
import random
import time
################################################################################
import config
import argparse
################################################################################
from helpers import RSSContentHelper, FeedSetHelper
from twitter import Twitter
from models import FeedSet,create_tables
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
################################################################################
# Third Party Libraries
import tweepy

class BypassAntiBot:
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def bypass(self):
        try:
            print("Bypass anti-bot protections ...")
            self.randomretweet()
            self.randomtweet()
            print("Anti-bot bypass completed !")

        except tweepy.TweepError as e:
            if e.api_code == 326:
                pass

    def calcul_randomrt(self):
        print("Vérification des RT concours")
        follow_count, retweet_count = 0, 0
        for tweet in self.api.user_timeline(count=200, tweet_mode="extended"):
            if tweet.retweeted:
                retweet_count += 1
                if "FOLLOW" in tweet.full_text.upper():
                    follow_count += 1
        ratio_RtFol = (follow_count * 100) / retweet_count
        if ratio_RtFol > 25:
            #randomrtobjectif = retweet_count * 4
            #randomrt = randomrtobjectif - follow_count
            randomrt = (retweet_count * 4) - follow_count
            print("Il y a " + str(ratio_RtFol) + " % de RT pour les concours on va faire " + str(randomrt) + " RT random")
        else:
            print("Il y a " + str(ratio_RtFol) + " % de RT pour les concours on passe a la suite.")
            randomrt = 0
        return randomrt

    def calcul_randomtweet(self):
        print("Vérification des RT")
        follow_count, retweet_count = 0, 0
        for tweet in self.api.user_timeline(count=200, tweet_mode="extended"):
            if tweet.retweeted:
                retweet_count += 1

        if retweet_count > 100:
            print("actuellement il y a " + str(retweet_count) + " retweets pour 200 tweets il faut faire " + str(nb_randomtweet) + "tweets random")
            nb_randomtweet =  retweet_count - 100
            if nb_randomtweet > 10:
                nb_randomtweet =  10
                print("On va tweets uniquement " + str(nb_randomtweet) + " pour l'instant")
        else:
            print("Il y a moins de 50% de ReTweets sur le compte on passe a la suite")
            nb_randomtweet =  0
        return nb_randomtweet

    def randomretweet(self):
        randomrt = self.calcul_randomrt()
        trend_api_response = self.api.trends_place(615702)
        trends = list([trend['name'] for trend in trend_api_response[0]['trends']])
        while randomrt > 0:
            random_count = random.randrange(0, len(trends))
            for tweet in tweepy.Cursor(self.api.search,
                                    q=trends[random_count],
                                    result_type="popular",
                                    include_entities="True",
                                    lang="fr").items(randomrt):
                try:
                    tweet.retweet()
                    time.sleep(random.randrange(120, 180))
                    randomrt -= 1
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

    def randomtweet(self):
        try:
            nb_randomtweet = self.calcul_randomtweet()
            account = self.account
            print("Tweet a faire : " + str(nb_randomtweet))
            while nb_randomtweet > 0:
                getfeeds(self.account)
                tweet(self.account)
                time.sleep(random.randrange(120, 150))
                nb_randomtweet -= 1
        except tweepy.TweepError as e:
            if e.api_code == 185:
                print("Message en attente, on a envoyé trop de message")
                time.sleep(1500)
            elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186) or (e.api_code == 326):
                pass
            else:
                print(e.reason)
################################################################################
@contextmanager
def session_scope(account):
    """Provide a transactional scope around a series of operations."""
    session = db_session(account)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def db_session(account):
    db_path = 'databases/rss_{}.db'.format(account)
    engine = create_engine("sqlite:///{}".format(db_path))
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def getfeeds(account):
    create_tables(account)
    with session_scope(account) as session:
        helper = FeedSetHelper(session, account)
        helper.get_pages_from_feeds()

def tweet(account):
    with session_scope(account) as session:
        helper = RSSContentHelper(session, account)
        rsscontent = helper.get_oldest_unpublished_rsscontent(session)
        if(rsscontent):
            helper.tweet_rsscontent(rsscontent)
