# BotTwitter
Un bot multi-compte Twitter simple d'utilisation pour participer aux concours.


### Les fonctionnalités du bot :

* Multicompte
* Bypass les protections de Pickaw (Twrench)
* Tag des comptes quand un concours le demande
* Retweet, like et follow les concours
* Unfollow automatique
* Possibilité de blacklist des comptes


### Dépendance du script :

Vous devez installer cette librairie pour que le script fonctionne.
```
Tweepy
```
### Installation :

* Dans un premier temps pour utiliser le script vous allez avoir besoin d'un compte développeur Twitter et de récupérer vos accès à l'API.
 Vous pouvez demander cet accès sur le site développeur de Twitter : [Twitter Developer](https://developer.twitter.com/)

* Vous devez ensuite installer une version 3.x de Python : [Python 3.x](https://www.python.org/downloads/)

* Et pour finir vous devez installer la librairie Tweepy (Pour pouvoir communiquer avec l'API Twitter plus facilement) : [tweepy](https://www.tweepy.org/).
 Pour vous faciliter les choses vous pouvez l'installer avec pip3 (pour python3).
 Et faire la commande dans votre console (cmd pour Windows) : 
 ```
 python3 -m pip install tweepy
 ou
 py -m pip install tweepy
 ```
 Si pip n'est pas reconnu vous devez l'installer.


### Configuration :

Une fois le script téléchargé, vous devez rentrer les clés de l'[API Twitter](https://developer.twitter.com/) dans le dictionnaire "compte" du fichier main.py.
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
Pour lancer le bot vous devez faire : 
```
python3 main.py
ou
py main.py
```


Vous avez une question ? Des idees d'ameliorations ?  Mon nom d'utilisateur twitter est : @j4rj4r_binks
