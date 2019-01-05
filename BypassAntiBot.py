import tweepy,random,time

def bypass(api) :#Fonction principal de bypass anti bot (basé sur le site twren.ch)
    user = api.me()
    print("Bypass pour le compte : " + user.name)
    nb = 1
    pourcentageRTFollow = CalculPourcentageRtFollow(api)
    while pourcentageRTFollow >= 25 : #On veut moins de 25% de RT avec le mot Follow
        randomretweet(api)
        pourcentageRTFollow = CalculPourcentageRtFollow(api)
        print("Pourcentage de Rt avec le mot Follow (en cours de diminution) : " + str(pourcentageRTFollow))
    print("Pourcentage de Rt avec le mot Follow (final) : " + str(pourcentageRTFollow))

    pourcentageRT = CalculPourcentageRT(api)
    while pourcentageRT >= 50 : #On veut moins de 50% de RT
        randomtweet(api)
        pourcentageRT = CalculPourcentageRT(api)
        nb += 1
    print("Pourcentage RT final : " + str(pourcentageRT))

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
    randommessage = ["#ILOVENICE","Nice","#photographie","YOLO","#Tesla","OGCNICE","Surprise","manger","rire","France","tv","chat","matin","Paris","Monde","fatigue","orthographe","chien","#photo","#voyage","#France"]
    nbrandom =  random.randrange(0,len(randommessage))
    for tweet in tweepy.Cursor(api.search,q=randommessage[nbrandom],result_type="recent",lang="fr").items(10):
        try:
            tweet.retweet()
        except tweepy.TweepError as e:
            if e.api_code == 185 :
                print("Message en attente, on a envoyé trop de message")
                time.sleep(1500)
            else :
                print(e.reason)
        except StopIteration:
            break


def randomtweet(api) : #On tweet un message
    try:
        f = open('randomtweet.txt','r', encoding="utf-8")
        t = f.readlines()
        f.close()
        nbrandom =  random.randrange(0,len(t))
        nbrandom2 = random.randrange(0,1500)
        message = t[nbrandom]
        api.update_status(message + str(nbrandom2))#On ajoute nombre random pour éviter probleme dupli (à vérifier)
    except tweepy.TweepError as e:
        if e.api_code == 185 :
            print("Message en attente, on a envoyé trop de message")
            time.sleep(1500)
        else :
            print(e.reason)
