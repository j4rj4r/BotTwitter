import tweepy,random,time

def bypass(api) :#Fonction principal de bypass anti bot (basé sur le site twren.ch)
    user = api.me()
    print("Bypass pour le compte : " + user.name)
    nb = 1
    pourcentageRTFollow = CalculPourcentageRtFollow(api)
    while pourcentageRTFollow >= 25 : #On veut moins de 25% de RT avec le mot Follow
        randomretweet(api)
        pourcentageRTFollow = CalculPourcentageRtFollow(api)
        print("Pourcentage de Rt avec le mot Follow (en cours de diminution) : " + str(round(pourcentageRTFollow, 2)))
    print("Pourcentage de Rt avec le mot Follow (final) : " + str(round(pourcentageRTFollow, 2)))

    pourcentageRT = CalculPourcentageRT(api)
    while pourcentageRT >= 50 : #On veut moins de 50% de RT
        randomtweet(api)
        pourcentageRT = CalculPourcentageRT(api)
        nb += 1
    print("Pourcentage RT final : " + str(round(pourcentageRT, 2)))

def CalculPourcentageRT(api) : #Fonction calcul pourcentage RT  de l'utilisateur
    nb = 0
    for tweet in api.user_timeline(count=200, tweet_mode="extended") :
        if tweet.retweeted == True :#Si le tweet est un RT
            nb += 1
    pourcentage = (nb * 100)/200 #Calcul pourcentage
    return pourcentage

def CalculPourcentageRtFollow(api) : #Fonction calcul pourcentage de RT avec le mot Follow
    nb = 0
    nbrt = 0
    for tweet in api.user_timeline(count=200, tweet_mode="extended") :
        if tweet.retweeted == True :
            nbrt += 1
            if "FOLLOW" in tweet.full_text.upper() : #On met tout le texte en majuscule et n cherche le mot follow dans le tweet
                nb += 1
    pourcentage = (nb * 100)/nbrt
    return pourcentage

def randomretweet(api) : #On retweet un tweet random
    randomsearch = ["#Paris","Dance","#Fiesta","#ILOVENICE","Nice","#photographie","YOLO","#Tesla","OGCNICE","Surprise","manger","rire","France","tv","chat","matin","Paris","Monde","fatigue","orthographe","chien","#photo","#voyage","#France","#Travel"]
    nbrandom =  random.randrange(0,len(randomsearch))
    for tweet in tweepy.Cursor(api.search,q=randomsearch[nbrandom],result_type="recent",lang="fr").items(10):
        try:
            tweet.retweet()
        except tweepy.TweepError as e:
            if e.api_code == 185 :
                print("Message en attente, on a envoyé trop de message")
                time.sleep(1500)
            elif e.api_code == 327 :
                pass
            else :
                print(e.reason)
        except StopIteration:
            break


def randomtweet(api) : #On récupère un message tweeter et on le tweet
    try:
        randomsearch1 = ["#Paris","Champion","pizza","#écologie","pizza","#drone","Amour","#photographie","YOLO","#Tesla","Surprise","manger","rire","France","tv","chat","matin","drole","radio","Paris","Monde","fatigue","orthographe","boulot","dodo","cocacola","pepsi","fiesta","chien","#photo","#voyage","#France","#Travel","Tournoi","Tennis","Sport","foot","badminton","vacance","valise","monde","tatouage","#paranormal","#fun","Cote d'azur","Cinéma","théatre","montagne","Bretagne"]
        nbrandom =  random.randrange(0,len(randomsearch1))
        for tweet in tweepy.Cursor(api.search,q=randomsearch1[nbrandom],lang="fr",tweet_mode="extended",result_type='recent').items(1):
            if hasattr(tweet, 'retweeted_status') :
                tweettext = tweet.retweeted_status.full_text
                if "@" in tweettext : #On évite de notifier les gens quand on récupère un tweet d'un autre
                    tweettext = tweettext.replace("@"," ")
                api.update_status(tweettext)
                time.sleep(10)
            else :
                tweettext = tweet.full_text
                if "@" in tweettext :
                    tweettext = tweettext.replace("@"," ")
                api.update_status(tweettext)
                time.sleep(10)
    except tweepy.TweepError as e:
        if e.api_code == 185 :
            print("Message en attente, on a envoyé trop de message")
            time.sleep(1500)
        elif (e.api_code == 187) or (e.api_code == 327) or (e.api_code == 186):
            pass
        else :
            print(e.reason)
