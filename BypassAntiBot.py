#Bibliothèques standard
import random
import time

#Bibliothèques tierces
import tweepy

#Fonction principal de bypass anti bot (basé sur le site twren.ch)
def bypass(api):
    try:
        print("Bypass des protections Pickaw en cours")
        nb = 1
        pourcentageRTFollow = CalculPourcentageRtFollow(api)
        #On veut moins de 25% de RT avec le mot Follow
        while pourcentageRTFollow >= 25:
            randomretweet(api)
            pourcentageRTFollow = CalculPourcentageRtFollow(api)
            print("Pourcentage de Rt avec le mot Follow (en cours de diminution) : " + str(round(pourcentageRTFollow, 2)))
        print("Pourcentage de Rt avec le mot Follow (final) : " + str(round(pourcentageRTFollow, 2)))
        pourcentageRT = CalculPourcentageRT(api)
        #On veut moins de 50% de RT
        while pourcentageRT >= 50:
            randomtweet(api)
            pourcentageRT = CalculPourcentageRT(api)
            nb += 1
        print("Pourcentage RT final : " + str(round(pourcentageRT, 2)))
    except tweepy.TweepError as e:
        if e.api_code == 326:
            pass

#Fonction calcul pourcentage RT  de l'utilisateur
def CalculPourcentageRT(api):
    nb = 0
    for tweet in api.user_timeline(count=200, tweet_mode="extended"):
        #Si le tweet est un RT
        if tweet.retweeted:
            nb += 1
    #Calcul pourcentage
    pourcentage = (nb * 100)/200
    return pourcentage

#Fonction calcul pourcentage de RT avec le mot Follow
def CalculPourcentageRtFollow(api):
    nb = 0
    nbrt = 0
    for tweet in api.user_timeline(count=200, tweet_mode="extended"):
        if tweet.retweeted:
            nbrt += 1
            if "FOLLOW" in tweet.full_text.upper(): #On met tout le texte en majuscule et n cherche le mot follow dans le tweet
                nb += 1
    pourcentage = (nb * 100)/nbrt
    return pourcentage

def randomretweet(api): #On retweet un tweet random
    trends1 = api.trends_place(610264)
    trends = list([trend['name'] for trend in trends1[0]['trends']])
    nbrandom = random.randrange(0, len(trends))
    for tweet in tweepy.Cursor(api.search, q=trends[nbrandom], result_type="recent", lang="fr").items(10):
        try:
            tweet.retweet()
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

#On récupère un message twitter et on le tweet
def randomtweet(api):
    try:
        #Code France (marseille) FR
        trends1 = api.trends_place(610264)
        #On récupère la liste des tendances
        trends = list([trend['name'] for trend in trends1[0]['trends']])
        nbrandom = random.randrange(0, len(trends))
        #On cherche des tweets parmis les tweets recents
        for tweet in tweepy.Cursor(api.search, q=trends[nbrandom] + " -filter:replies -filter:media -filter:retweets", lang="fr", tweet_mode="extended", result_type='recent').items(1):
            if hasattr(tweet, 'retweeted_status'):
                #On ne veut pas tweet un concours
                if "CONCOURS" in tweet.retweeted_status.full_text.upper():
                    pass
                else:
                    tweettext = tweet.retweeted_status.full_text
                    #On évite de notifier les gens quand on récupère un tweet d'un autre
                    if "@" in tweettext:
                        tweettext = tweettext.replace("@", " ")
                    #On évite les # pour etre discret
                    if "#" in tweettext:
                        tweettext = tweettext.replace("#", " ")
                    api.update_status(tweettext)
            else:
                #On ne veut pas tweet un concours
                if "CONCOURS" in tweet.full_text.upper():
                    pass
                else:
                    tweettext = tweet.full_text
                    if "@" in tweettext:
                        tweettext = tweettext.replace("@", " ")
                    if "#" in tweettext:
                        tweettext = tweettext.replace("#", " ")
                    api.update_status(tweettext)
            time.sleep(20)
    except tweepy.TweepError as e:
        if e.api_code == 185:
            print("Message en attente, on a envoyé trop de message")
            time.sleep(1500)
        elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186) or (e.api_code == 326):
            pass
        else:
            print(e.reason)
