import tweepy,RetweetConcours,BypassAntiBot,time,random,sys,GestionFollow
tabname = []

###Constante Paramètre du bot ###
version = 2.8 #Version du bot
compte = {"1":["","","",""],"2":["","","",""],"3":["","","",""],"4":["","","",""]} #Liste des comptes avec les identifiants de connexion à l'api
NombreDeRetweet = 12 #Nombre de tweet que l'on recupère par recherche
listerecherchefr = ["#concours","#JeuConcours","RT & Follow","tenter de gagner","Gagnez rt + follow","concours pour gagner"]#Mot à retweeté pour un concours
BlackListCompte = ["NistikConcours","WqveConcours","FlawyxC","Linyz_V1","FortniteVenox","TidaGameuse","YeastLeaks","CrashqConcours","Yanteh_","NistiKTV",]#Blacklist pour compte à concours (très) bidon | Il faut metre le pseudo après le @
CompteTag = ["@j4rj4r_binks"]#Les comptes à utiliser pour tag. Si vous utilisez plusieurs comptes bot vous n'avez pas besoins d'ajouter de comptes dans ce tableau. Vous devez rentrer le compte avec son @ (@toto)
###

for cle,tabauth in compte.items():
    try :
        auth = tweepy.OAuthHandler(tabauth[0], tabauth[1]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
        auth.set_access_token(tabauth[2], tabauth[3]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
        api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Authentification
        user = api.me()
        tabname.append("@" + user.screen_name)
        GestionFollow.CreateTables(user)
    except tweepy.TweepError as e:
        if e.api_code == 326 :
            print("Le compte " + cle + " est bloqué !")
        else :
            print(e.reason)
tabname = tabname + CompteTag

while True :
    for tabauth in compte.values(): #Pour chaque compte on passe dans cette boucle
        try :
            auth = tweepy.OAuthHandler(tabauth[0], tabauth[1]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
            auth.set_access_token(tabauth[2], tabauth[3]) #Authentification avec les valeurs du tableau trouvées dans le dictionnaire
            api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Authentification
            user = api.me()
            GestionFollow.Unfollow(user,api)
            RetweetConcours.retweet(api,NombreDeRetweet,listerecherchefr,tabname,BlackListCompte,CompteTag)#on retweet les concours
            BypassAntiBot.bypass(api)#On bypass l'anti bot
        except tweepy.TweepError as e :
            if e.api_code == 326 :
                pass
    nbrandom = random.randrange(2800,3500)
    try :
        print("Programme en attente de : " + str(nbrandom) + " s") #Temps d'attente en seconde avant une nouvelle boucle
        time.sleep(nbrandom)
    except tweepy.TweepError as e:
        if e.api_code == 326 :
            pass
    except KeyboardInterrupt : #On termine le programme proprement en cas de ctrl-c
        print("Programme terminé !")
        sys.exit()
