import tweepy,RetweetConcours,BypassAntiBot,time,random,sys
tabname = []

###Constante Paramètre du bot ###
version = 2.0 #Version du bot
compte = {"1":["","","",""],"2":["","","",""],"3":["","","",""]} #Liste des comptes avec les identifiants de connexion à l'api
NombreDeRetweet = 9 #Nombre de tweet que l'on recupère par recherche
listerecherchefr = ["#concours","#JeuConcours","RT & Follow","tenter de gagner","tirage au sort","Gagnez rt + follow","concours pour gagner"]#Mot à retweeté pour un concours
###
for tabauth in compte.values():
    auth = tweepy.OAuthHandler(tabauth[0], tabauth[1]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
    auth.set_access_token(tabauth[2], tabauth[3]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Authentification
    user = api.me()
    tabname.append("@" + user.screen_name)

while True :
    for tabauth in compte.values(): #Pour chaque compte on passe dans cette boucle
        auth = tweepy.OAuthHandler(tabauth[0], tabauth[1]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
        auth.set_access_token(tabauth[2], tabauth[3]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
        api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Authentification
        RetweetConcours.retweet(api,NombreDeRetweet,listerecherchefr,tabname)#on retweet les concours
        BypassAntiBot.bypass(api)#On bypass l'anti bot
    nbrandom = random.randrange(6500,7200)
    try :
        print("Programme en attente de : " + str(nbrandom) + " s") #Temps d'attente en seconde avant une nouvelle boucle
        time.sleep(nbrandom)
    except KeyboardInterrupt : #On termine le programme proprement en cas de ctrl-c
        print("Programme terminé !")
        sys.exit()
