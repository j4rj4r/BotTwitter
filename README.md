# BotTwitter
An easy-to-use multi-account Twitter bot to enter (and win) contests.

### The features :

* Multi-account
* Bypass the protections of Pickaw (Twrench)
* Tag of accounts when a contest requires it
* Retweet, like and follow contests
* Automatic unfollow
* You can blacklist accounts
* If the contest requires it the bot can follow several accounts
* The bot can respond to a contest with hashtags


### Requirements and Dependencies :

You must install [Python 3.x](https://www.python.org/downloads/) and these python3 libraries :
```
Tweepy
PyYaml
feedparser
```
### Installation :

* To use the script you will first need a Twitter developer account to get your API access.
 You can request this access on the Twitter developer site: [Twitter Developer](https://developer.twitter.com/)  
If you need a tutorial: : [Developer account tutorial](https://www.extly.com/docs/autotweetng_joocial/tutorials/how-to-auto-post-from-joomla-to-twitter/apply-for-a-twitter-developer-account/#apply-for-a-developer-account)

* You must install a version 3.x of Python : [Python 3.x](https://www.python.org/downloads/)

* Finally you need to install the libraries:
     ```
     python3 -m pip install -r requirements.txt
     ou
     py -m pip install tweepy -r requirements.txt
     ```
These commands are to be entered in your console (cmd for Windows).
 If pip is not recognized you must install it.


### Configuration :

All configuration settings are in the **configuration.yml** file.  
Copy the **configuration.yml.dist** file to create the **configuration.yml** file.

Once you have downloaded the project, to be able to run the script you need to add in the configuration.yml file the keys of the [Twitter API](https://developer.twitter.com/).
```
accounts:
  # Accounts name
  - "Nom du compte":
      # API key
      - "Example"
      # API key secret
      - "Example"
      # Access token
      - "Example"
      # Access token secret
      - "Example"
```
You can add as many accounts as you want.
```
accounts:
  # Accounts name
  - "Nom du compte":
      # API key
      - "Example"
      # API key secret
      - "Example"
      # Access token
      - "Example"
      # Access token secret
      - "Example"
  - "Nom du compte 2":
      # API key
      - "Example"
      # API key secret
      - "Example"
      # Access token
      - "Example"
      # Access token secret
      - "Example"
```
Pour faire fonctionner correctement la fonction de bypass antibot, vous devez renseigner des flux rss.  
Une liste de flux que vous pouvez ajouter est disponible ici : [Flux rss](http://atlasflux.saynete.net/index.htm)
```
# RSS
flux_rss:
    - https://partner-feeds.20min.ch/rss/20minutes
    - https://www.24matins.fr/feed
```

Il est possible désactiver la fonction de bypass antibot, la fonction like des concours, la fonction commenter avec un hashtag.
```
# Use the antibot bypass feature (True/False)
bypass_antibot : True

# Like all giveaway (True/False)
like_giveaway : False

# Comment with hashtag (True/False)
comment_with_hashtag : True
```

Vous pouvez ajouter des mot à rechercher pour trouver des concours
```
# Words to search for giveaway
words_to_search:
  - "#concours"
  - "#JeuConcours"
  - "concours pour gagner"
  - "Gagnez rt + follow"
  - "RT & follow"
```

Vous pouvez définir des comptes à tag quand un concours le demande (par défaut vos bots peuvent se tag entre eux)
```
# Accounts we want to invite
accounts_to_tag:
  - "@j4rj4r_binks"
```

En copiant des tweets, vous pouvez récupéré des tweets "sensibles". Il y a donc la possibilité de filtrer des mots à ne pas copier.
```
# Words that should not be copied with the antibot
words_to_blacklist_antibot:
  - "pd"
  - "tapette"
  - "enculé"
  - "pédale"
  - "isis"
```


# Notifications / Alerters

1. Dans le fichier de configuration, assurez vous que vous avez activé les alertes.
    ```
    be_notify_by_alerters : True
    ```

2. Configurer le ou les alertes que vous souhaitez:

    ```
    ---
    alerters:
      discord:
        webhook_url: https://discord.com/api/webhooks/XXXXXXXXXXXX...
        mentions:
          - XXXXXXXXXXXXXXX
          - XXXXXXXXXXXXXXX
      telegram:
        webhook_url: https://api.telegram.org/botXXXXXXXXXXXXXXXXXXXX/sendMessage
        chat_id: XXXXXXXX
      email:
        sender: myemail@email.com
        recipients:
          - myemail@email.com
          - myfriendsemail@email.com
        relay: 127.0.0.1
        password: XXXXXXXXXX   # optional
      slack:
        webhook_url: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
        mentions:
          - XXXXXXXXXXXXXXX
          - XXXXXXXXXXXXXXX
    ...
    ```


### Lancement du bot :
```
python3 main.py [--standalone]
ou
py main.py [--standalone]
```
--standalone est un paramètre optionnel permetant d'éxéctuter directement le bot sans interactivité.

Vous avez une question ? Des idées d'ameliorations ? vous pouvez venir sur notre serveur discord  : [MoneyMakers](https://discord.gg/gjNbrgwRxT)
On recherche des devs pour continuer à améliorer ce bot et à commencer de nouveaux projets !
