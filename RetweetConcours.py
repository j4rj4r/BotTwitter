import tweepy,random,BypassAntiBot,time,re

def retweet(api,NombreDeRetweet,listerecherchefr,tabname,BlackListCompte) :#Fonction de retweet de concours
    for mot in listerecherchefr : #Pour chaque mot dans la liste un lance une recherche
        for tweet in tweepy.Cursor(api.search,q=mot + " since:" + time.strftime('%Y-%m-%d',time.localtime()),lang="fr",tweet_mode="extended").items(NombreDeRetweet): #On cherche avec #concours parmis les plus populaires en france
            try:
                if tweet.retweet_count > 5 :
                    if hasattr(tweet, 'retweeted_status') : #Si le tweet est un retweet ou pas
                        if(tweet.retweeted_status.author.screen_name in BlackListCompte) : #Si l'utilisateur est dans la blacklist on fait rien.
                            print("Compte blacklist : " + tweet.retweeted_status.author.screen_name)
                            pass
                        else :
                            tweet.retweet() #On retweet
                            tweet.favorite()  #On like
                            api.create_friendship(tweet.retweeted_status.author.id)
                            print('Vous avez retweet le tweet de  @' + tweet.retweeted_status.author.screen_name)
                    else :
                        if(tweet.user.screen_name in BlackListCompte) :
                            print("Compte blacklist : " + tweet.user.screen_name)
                            pass
                        else :
                            tweet.retweet() #On retweet
                            tweet.favorite() #On like
                            api.create_friendship(tweet.user.id) #On follow
                            print('Vous avez retweet le tweet de  @' + tweet.user.screen_name)
                    if re.search("(^|\s|#)INVIT[É|E](|R|Z)\s", tweet.full_text.upper()) : #On vérifie avec une expression régulière si il faut inviter des amies.
                        commentaire(api,tweet,tabname)
                    elif re.search("(^|\s|#)TAG(|UE|UER|UEZ|UÉ|É)\s", tweet.full_text.upper()) : #On vérifie si il faut inviter des amies.
                        commentaire(api,tweet,tabname)
                    elif re.search("(^|\s|#)MENTIONN[É|E](|Z|R)\s", tweet.full_text.upper()) : #On vérifie si il faut inviter des amies.
                        commentaire(api,tweet,tabname)
                BypassAntiBot.randomtweet(api)
            except tweepy.TweepError as e:
                if e.api_code == 185 :
                    print("Message en attente, on a envoyé trop de message :(")
                    time.sleep(1500)
                elif (e.api_code == 327) or (e.api_code == 139) :
                    pass
                else :
                    print(e.reason)
            except StopIteration:
                break

def commentaire(api,tweet,tabname) : #Fonction pour faire un commentaire
    try:
        if hasattr(tweet, 'retweeted_status') :
            comment = "@" + tweet.retweeted_status.author.screen_name + " J'invite : "
        else :
            comment = "@" + tweet.user.screen_name + " J'invite : " #On prepare le message de commentaire
        user = api.me()
        nbusernotif = 0 #Variale compteur de compte tag
        random.shuffle(tabname) #On mélange le tableau aléatoirement.
        for username in tabname :
            if username == "@" + user.screen_name : #On veut pas mentionner le compte actif.
                username = ""
            if nbusernotif < 2 : #On veut pas tag plus de 2 comptes
                comment = comment + username + " " #On fait le message de commentaire
                nbusernotif +=1 # On augmente le compteur de compte tag
        if hasattr(tweet, 'retweeted_status') :
            api.update_status(comment,tweet.retweeted_status.id)
        else :
            api.update_status(comment,tweet.id) #On envoit le commentaire
    except tweepy.TweepError as e:
        if e.api_code == 185 :
            print("Message en attente, on a envoyé trop de message")
            time.sleep(1500)
        else :
            print(e.reason)
