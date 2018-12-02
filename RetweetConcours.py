import tweepy

def retweet(api,NombreDeRetweet,listerecherchefr,tabname) :#Fonction de retweet de concours
    for mot in listerecherchefr : #Pour chaque mot dans la liste un lance une recherche
        for tweet in tweepy.Cursor(api.search,q=mot,lang="fr",tweet_mode="extended").items(NombreDeRetweet): #On cherche avec #concours parmis les plus populaires en france
            try:
                if tweet.retweet_count > 5 :
                    tweet.retweet() #On retweet
                    if hasattr(tweet, 'retweeted_status') :
                        api.create_friendship(tweet.retweeted_status.author.id)
                        print('Vous avez retweet le tweet de  @' + tweet.retweeted_status.author.screen_name)
                    else :
                        api.create_friendship(tweet.user.id) #On follow
                        print('Vous avez retweet le tweet de  @' + tweet.user.screen_name)
                    if "INVITER" in tweet.full_text.upper() : #On vérifie si il faut inviter des amies.
                        commentaire(api,tweet,tabname)
                    elif "MENTIONNE" in tweet.full_text.upper() : #On vérifie si il faut inviter des amies.
                        commentaire(api,tweet,tabname)
            except tweepy.TweepError as e:
                print(e.reason)
            except StopIteration:
                break

def commentaire(api,tweet,tabname) :
    try:
        comment = "@" + tweet.user.screen_name + " J'invite : " #On prepare le message de commentaire
        user = api.me()
        for username in tabname :
            if username == "@" + user.screen_name : #On veut pas mentionner le compte actif.
                username = ""
            comment = comment + username + " " #On fait le message de commenataire
        api.update_status(comment,in_reply_to_status=tweet.id) #On envoit le commentaire
    except tweepy.TweepError as e:
        print(e.reason)
