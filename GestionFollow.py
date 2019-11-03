import sqlite3,datetime

def CreateTables(user) :
    connexion = sqlite3.connect('data.db') #On crée data.db ou on l'ouvre juste si elle existe
    c = connexion.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS {tab}
    (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, compte text, date DATE);'''.format(tab=user.screen_name)) #On fait une table pour chaque compte
    c.close()
    connexion.commit()


def UpdateTable(follower,user) :
    connexion = sqlite3.connect('data.db')
    c = connexion.cursor()
    c.execute('''SELECT * FROM {tab} WHERE compte = ?;'''.format(tab=user.screen_name),(str(follower),)) #On regarde si on a déjà un follower avec cet id
    data=c.fetchall()
    if len(data)==0:
        c.execute('''INSERT INTO {tab}(compte,date) VALUES (:compte, :date);'''.format(tab=user.screen_name),(follower,datetime.datetime.now())) #On rentre la date du jour et le compte follow
        c.close()
        connexion.commit()
    else:
        c.execute('''UPDATE {tab} SET date = ? WHERE compte = ?'''.format(tab=user.screen_name),(datetime.datetime.now(),str(follower),)) #On change la date
        c.close()
        connexion.commit()



def Unfollow(user,api) :
    print("Vérification des comptes à unfollow.")
    connexion = sqlite3.connect('data.db') #On crée data.db ou on l'ouvre juste si elle existe
    c = connexion.cursor()
    c.execute('''SELECT * FROM {tab};'''.format(tab=user.screen_name)) #On selectionne toute la table
    data=c.fetchall()
    for i in data:
        date = datetime.datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S.%f")
        if date.month == 11 :
            newmonth = 1
        elif date.month == 12 :
            newmonth = 2
        else :
            newmonth = date.month+2
        date = date.replace(month=newmonth)
        if datetime.datetime.now() > date :
            api.destroy_friendship(i[1])
            c.execute('''DELETE FROM {tab} WHERE compte = ?;'''.format(tab=user.screen_name),(str(i[1]),))
        else :
            pass
    c.close()
    connexion.commit()
