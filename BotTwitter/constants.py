def init():
    global VERSION, CONFIGURATION_FILE, DB_FILE, APP_NAME
    APP_NAME = 'Bot Twitter'
    VERSION = '3.0.0'
    CONFIGURATION_FILE = 'configuration.yml'
    DB_FILE = "_BotTwitter_.db"

    # Regex
    global regex_detect_tag, regex_detect_like, regex_detect_comment, regex_detect_rt, regex_detect_follow
    regex_detect_tag = [r'\b(\w*INVIT(E|É)\w*)\b',
                        r'\b(\w*IDENTIFI(E|É)\w*)\b',
                        r'\b(\w*TAG\w*)\b',
                        r'\b(\w*MENTIONN(E|É)\w*)\b']

    regex_detect_like = [r'\b(\w*LIK(E|EZ)\w*)\b',
                         r'\b(\w*FAV\w*)\b',
                         r"\b(\w*AIME\w*)\b"]

    regex_detect_comment = [r'\b(\w*COMMENT(E|EZ)\w*)\b',
                            r'\b(\w*REPONSE\w*)\b']

    regex_detect_rt = [r'\b(\w*RT\w*)\b',
                       r'\b(\w*RETWEET\w*)\b',
                       r'\b(\w*PARTAGE\w*)\b', ]

    regex_detect_follow = [r'\b(\w*SUIV(RE|EZ)\w*)\b',
                           r'\b(\w*FOLLOW\w*)\b']
