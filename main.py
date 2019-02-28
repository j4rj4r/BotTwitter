import tweepy,RetweetConcours,BypassAntiBot,time,random,sys
tabname = []

###Constante Paramètre du bot ###
version = 2.5 #Version du bot
compte = {"1":["","","",""],"2":["","","",""],"3":["","","",""],"4":["","","",""]} #Liste des comptes avec les identifiants de connexion à l'api
NombreDeRetweet = 12 #Nombre de tweet que l'on recupère par recherche
listerecherchefr = ["#concours","#JeuConcours","RT & Follow","tenter de gagner","Gagnez rt + follow","concours pour gagner"]#Mot à retweeté pour un concours
BlackListCompte = ["NistikConcours","WqveConcours","FlawyxC","Linyz_V1","FortniteVenox","TidaGameuse","YeastLeaks","CrashqConcours","Yanteh_","NistiKTV",]#Blacklist pour compte à concours (très) bidon | Il faut metre le pseudo après le @
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
        RetweetConcours.retweet(api,NombreDeRetweet,listerecherchefr,tabname,BlackListCompte)#on retweet les concours
        BypassAntiBot.bypass(api)#On bypass l'anti bot
    nbrandom = random.randrange(3000,3500)
    try :
        print("Programme en attente de : " + str(nbrandom) + " s") #Temps d'attente en seconde avant une nouvelle boucle
        time.sleep(nbrandom)
    except KeyboardInterrupt : #On termine le programme proprement en cas de ctrl-c
        print("Programme terminé !")
        sys.exit()
