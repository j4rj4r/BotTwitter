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
     or
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
To make the antibot bypass function work properly, you need to add rss feeds to the configuration file.  
A list of feeds you can add is available here: [Flux rss](http://atlasflux.saynete.net/index.htm)
```
# RSS
flux_rss:
    - https://partner-feeds.20min.ch/rss/20minutes
    - https://www.24matins.fr/feed
```

### How to run :
```
python3 main.py [--standalone]
or
py main.py [--standalone]
```
--standalone is an optional parameter allowing to run the bot without interactivity.

You have a question ? Ideas for improvements ? You can come on our discord server : [MoneyMakers](https://discord.gg/gjNbrgwRxT)