#Bibliothèques standard
import time
import random
import re

#Bibliothèques tierces
import tweepy

#Imports locaux
import BypassAntiBot
import GestionFollow

#Fonction qui permet de trouver et de retweet,like et follow les concours
def retweet(user, api, NombreDeRetweet, listerecherchefr, tabname, BlackListCompte):
    #Pour chaque mot dans la liste un lance une recherche
    for mot in listerecherchefr:
        print("Recherche avec le mot : " + mot)
        #On cherche des concours en fonction de la date du jour et de la langue
        for tweet in tweepy.Cursor(api.search, q=mot + " since:" + time.strftime('%Y-%m-%d', time.localtime()), lang="fr", tweet_mode="extended").items(NombreDeRetweet):
            try:
                if tweet.retweet_count > 5:
                    #Si le tweet est un retweet ou pas
                    if hasattr(tweet, 'retweeted_status'):
                        #Si l'utilisateur est dans la blacklist on fait rien.
                        if(tweet.retweeted_status.author.screen_name in BlackListCompte):
                            print("Compte blacklist : " + tweet.retweeted_status.author.screen_name)
                        #On évite de retweet et follow les tweets en rapport avec le follow back
                        elif "BACK" in tweet.retweeted_status.full_text.upper() :
                            pass
                        elif "JFB" in tweet.retweeted_status.full_text.upper() :
                            pass
                        else:
                            #On retweet
                            tweet.retweet()
                            #On like
                            tweet.favorite()
                            #On follow
                            api.create_friendship(tweet.retweeted_status.author.id)
                            print('Vous avez retweet le tweet de  @' + tweet.retweeted_status.author.screen_name)
                            #On met à jour la base de donnee
                            GestionFollow.UpdateTable(tweet.retweeted_status.author.id, user)
                            try:
                                #Permet de follow d'autres comptes si demandé
                                words = tweet.retweeted_status.full_text.split()
                                for word in words:
                                    if word.find('@') == 0:
                                        compte = word.replace('@', "")
                                        api.create_friendship(compte)
                                        GestionFollow.UpdateTable(compte, user)
                            except:
                                pass
                            #Si on nous demande d'inviter des amis
                            if re.search(r"\b(\w*INVIT(E|É)\w*)\b", tweet.retweeted_status.full_text.upper(), re.M): #On vérifie avec une expression régulière si il faut inviter des amies.
                                commentaire(user, api, tweet, tabname)
                            elif re.search(r"\b(\w*TAG\w*)\b", tweet.retweeted_status.full_text.upper(), re.M):
                                commentaire(user, api, tweet, tabname)
                            elif re.search(r"\b(\w*MENTIONN(E|É)\w*)\b", tweet.retweeted_status.full_text.upper(), re.M):#On vérifie si il faut inviter des amies.
                                commentaire(user, api, tweet, tabname)
                            BypassAntiBot.randomtweet(api)
                    #Si le tweet est le concours original
                    else:
                        if(tweet.user.screen_name in BlackListCompte):
                            print("Compte blacklist : " + tweet.user.screen_name)
                        #On évite de retweet et follow les tweets en rapport avec le follow back
                        elif "BACK" in tweet.full_text.upper() :
                            pass
                        elif "JFB" in tweet.full_text.upper() :
                            pass
                        else:
                            #On retweet
                            tweet.retweet()
                            #On like
                            tweet.favorite()
                            #On follow
                            api.create_friendship(tweet.user.id)
                            print('Vous avez retweet le tweet de  @' + tweet.user.screen_name)
                            GestionFollow.UpdateTable(tweet.user.id, user)
                            try:
                                words = tweet.full_text.split()
                                for word in words:
                                    if word.find('@') == 0:
                                        compte = word.replace('@', "")
                                        api.create_friendship(compte)
                                        GestionFollow.UpdateTable(compte, user)
                            except:
                                pass
                            #On vérifie avec une expression régulière si il faut inviter des amies.
                            if re.search(r"\b(\w*INVIT(E|É)\w*)\b", tweet.full_text.upper(), re.M):
                                commentaire(user, api, tweet, tabname)
                            elif re.search(r"\b(\w*TAG\w*)\b", tweet.full_text.upper(), re.M):
                                commentaire(user, api, tweet, tabname)
                            elif re.search(r"\b(\w*MENTIONN(E|É)\w*)\b", tweet.full_text.upper(), re.M):
                                commentaire(user, api, tweet, tabname)
                            BypassAntiBot.randomtweet(api)
            except tweepy.TweepError as e:
                if e.api_code == 185:
                    print("Message en attente, on a envoyé trop de message :(")
                    time.sleep(1250)
                elif (e.api_code == 327) or (e.api_code == 139) or (e.api_code == 326):
                    pass
                else:
                    print(e.reason)
            except StopIteration:
                break

#Fonction pour faire un commentaire
def commentaire(user, api, tweet, tabname):
    try:
        #Liste de debut de commentaire
        com = [" J'invite : ", " Merci ! je tag : ", " Je tag : ", " Hop Hop, j'invite : ",
               " Avec moi : ", " Help me : ", " Pour vous aussi les gars : ", " tentez votre chance ! : ",
               " Je tente ma chance ! J'espère que je vais gagner ! : ", " J'espère que vais gagner ! : ",
               " Merci pour le concours ! Essayez aussi : ", " Que la chance soit avec moi ! et vous ",
               " Merci d'organiser ce concours ! Ça peut vous intéresser ", " On croise les doigts ! vous aussi ",
               " C'est pour vous ça ! : ", " Celui là on le gagne ", " J'espère que vais gagner ! On participe ! ",
               " Merci d'organiser ce concours ! ", " Bonne chance à tous ! ", " J'adore les concours et je sais que vous aussi ",
               " J'ai tellement envie de gagner, essayez vous aussi ", " Je participe et j'invite "]
        nbrandom = random.randrange(0, len(com))
        comstart = com[nbrandom]
        if hasattr(tweet, 'retweeted_status'):
            comment = "@" + tweet.retweeted_status.author.screen_name + comstart
        else:
            #On prepare le message de commentaire
            comment = "@" + tweet.user.screen_name + comstart
        #Variale compteur de compte tag
        nbusernotif = 0
        #On mélange le tableau aléatoirement.
        random.shuffle(tabname)
        for username in tabname:
            #On veut pas tag plus de 2 comptes
            if nbusernotif < 2:
                #On veut pas mentionner le compte actif.
                if username == "@" + user.screen_name:
                    pass
                else:
                    #On fait le message de commentaire
                    comment = comment + username + " "
                    # On augmente le compteur de compte tag
                    nbusernotif += 1
        if hasattr(tweet, 'retweeted_status'):
            api.update_status(comment, tweet.retweeted_status.id)
        else:
            #On envoit le commentaire
            api.update_status(comment, tweet.id)
    except tweepy.TweepError as e:
        if e.api_code == 185:
            print("Message en attente, on a envoyé trop de message")
            time.sleep(1250)
        elif e.api_code == 326:
            pass
        else:
            print(e.reason)
