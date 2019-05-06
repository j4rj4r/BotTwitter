# BotTwitter
Un bot multi-compte Twitter simple d'utilisation pour participer aux concours.

### Dépendance du script :

Vous devez avec cette librairie pour que le script fonctionne.
```
Tweepy
```
Vous pouvez l'installer avec : pip install tweepy

### Installation :

Vous devez avoir [Python 3.0](https://www.python.org/download/releases/3.0/) et la librairie [tweepy](https://www.tweepy.org/) installé.
Une fois le script téléchargé, vous devez rentrer les clés de l'API [twitter](https://developer.twitter.com/) dans le dictionnaire "compte" du fichier main.py.
```
compte = {"1":[API key,API secret key,Access token,Access token secret]}
```
Vous pouvez rajouter autant de compte que vous voulez.
```
compte = {"1":[API key,API secret key,Access token,Access token secret],"2":[API key,API secret key,Access token,Access token secret]}
```

Vous pouvez choisir de participer à aucun concours d'un compte en le blacklistant. Vous avez juste à ajouter le @ du compte en question dans ce tableau.
```
BlackListCompte =["NistikConcours","WqveConcours","FlawyxC","Linyz_V1","FortniteVenox","TidaGameuse","YeastLeaks"]
```

Pour ajouter des comptes à tag quand un concours le demande, vous pouvez mettre les comptes dans ce tableau (Vous devez mettre obligatoirement le @) 

```
CompteTag = ["@j4rj4r_binks"]
```
Pour lancer le bot vous devez faire : python3 main.py

### Les fonctionnalités du bot :

* Multicompte
* Bypass les protections de Twrench
* Tag des comptes quand un concours le demande
* Retweet, like et follow les concours
* Unfollow automatique
* Possibilité de blacklist des comptes

Vous avez une question ? Mon nom d'utilisateur twitter est : @j4rj4r1
