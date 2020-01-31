# Bibliothèques standard
import time
import random
import sys

# Bibliothèques tierces
import tweepy

# Imports locaux
import RetweetConcours
import BypassAntiBot
import GestionFollow


### Constante Paramètre du bot ###
# Version du bot
VERSION = 2.9
# Liste des comptes avec les identifiants de connexion à l'api
COMPTE = {"1": ["", "", "", ""]}
# Nombre de tweet que l'on recupère par recherche
NOMBREDERETWEET = 12
# Mot à chercher pour trouver un concours
LISTERECHERCHEFR = ["#concours", "#JeuConcours", "RT & Follow", "tenter de gagner",
                    "Gagnez rt + follow", "concours pour gagner"]
# Liste des comptes qu'on blacklist (on ne participe pas à leurs concours)
# Il faut metre le pseudo sans le @
BLACKLISTCOMPTE = ["gulzaarAvi", "NistikConcours", "WqveConcours", "FlawyxC",
                   "Linyz_V1", "FortniteVenox", "TidaGameuse", "YeastLeaks",
                   "CrashqConcours", "Yanteh_", "NistiKTV", "BotSpotterBot",
                   "b0ttem", "RealB0tSpotter", "jflessauSpam", "ConcoursCool",
                   "GamingCRewards", "BotFett"]
# Les comptes à utiliser pour tag.
# Si vous utilisez plusieurs comptes bot vous n'avez pas besoins d'ajouter de comptes dans ce tableau.
# Vous devez rentrer le compte avec son @ (@toto)
COMPTETAG = ["@j4rj4r_binks"]
# Permet d'activer ou pas la fonction bypass Antibot (False pour désactiver, True pour activer)
BYPASSANTIBOT = True
###

tabname = []

# Permet de recuperer la liste des comptes qui sont utilises avec le script
for cle, tabauth in COMPTE.items():
    try:
        # Authentification avec les valeurs du tableau trouvées dans le dictionnaire
        auth = tweepy.OAuthHandler(tabauth[0], tabauth[1])
        # Authentification avec les valeurs du tableau trouvées dans le dictionnaire
        auth.set_access_token(tabauth[2], tabauth[3])
        # Authentification
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        user = api.me()
        tabname.append("@" + user.screen_name)
        GestionFollow.CreateTables(user)
    except tweepy.TweepError as error:
        if error.api_code == 326 or error.api_code == 32:
            print("Le compte " + cle + " a eu un probleme d'authentification !")
        else:
            print(error.reason)
tabname = tabname + COMPTETAG
print("--------------------------------------")

# Toujours vrai (boucle infinie)
while True:
    # Pour chaque compte on passe dans cette boucle
    for tabauth in COMPTE.values():
        try:
            # Authentification avec les valeurs du tableau trouvées dans le dictionnaire
            auth = tweepy.OAuthHandler(tabauth[0], tabauth[1])
            # Authentification avec les valeurs du tableau trouvées dans le dictionnaire
            auth.set_access_token(tabauth[2], tabauth[3])
            # Authentification
            api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
            user = api.me()
            print("Lancement du bot sur : " + user.screen_name)
            # On regarde si on doit unfollow des comptes
            GestionFollow.Unfollow(user, api)
            # on retweet les concours
            RetweetConcours.retweet(user, api, NOMBREDERETWEET, LISTERECHERCHEFR, tabname, BLACKLISTCOMPTE)
            if BYPASSANTIBOT :
              # On bypass l'anti bot
              BypassAntiBot.bypass(api)
            print("Bot terminé pour ce compte.")
            print("--------------------------------------")
        except tweepy.TweepError as error:
            if error.api_code == 326:
                pass
        except KeyboardInterrupt:
            print("Programme terminé !")
            sys.exit()

    # On génère un nombre aléatoire
    nbrandom = random.randrange(2500, 3250)
    try:
        # Temps d'attente en seconde avant une nouvelle boucle
        print("Programme en attente de : " + str(nbrandom) + " s")
        time.sleep(nbrandom)
    except tweepy.TweepError as error:
        if error.api_code == 326:
            pass
    # On termine le programme proprement en cas de ctrl-c
    except KeyboardInterrupt:
        print("Programme terminé !")
        sys.exit()
