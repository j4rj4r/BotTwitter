import sqlite3
from collections import namedtuple


def get_table_info(cursor, table):
    def get_columns():
        cursor.execute(f'pragma table_info({table})')
        return tuple((col[1], col[2]) for col in cursor.fetchall())

    cursor.execute(f"select * from sqlite_master where type='table' and name=?", (table,))
    tbl = cursor.fetchone()
    if tbl is None:
        return None
    cursor.execute(f'select count(*) from {table}')
    count = cursor.fetchone()
    return {
        'type': tbl[0],
        'name': tbl[1],
        'tbl_name': tbl[2],
        'rootpage': tbl[3],
        'sql': tbl[4],
        'columns': get_columns(),
        'rows_count': count[0]
    }


MASTER = 'sqlite_master'


class database:
    Users_row = namedtuple('Users_row', ('UserId', 'IdAccount', 'NameAccount'))
    Follows_row = namedtuple('Follows_row', ('FollowId', 'UserId', 'FollowIdAccount', 'DateFollow'))
    Stats_row = namedtuple('Stats_row', ('StatId', 'UserId', 'NbRetweet', 'NbTag'))
    Giveaways_row = namedtuple('Giveaways_row',
    ('GiveawayId', 'UserId', 'GiveawayUserId', 'GiveawayUsername', 'TweetId', 'TweetMessage', 'NeedTags', 'NeedComment', 'NeedLike', 'NeedFollow',   'NeedRt', 'DateBot', 'TagsBot', 'RtBot', 'FollowBot', 'LikeBot', 'CommentBot', 'PrivateMessage'))
    RSS_row = namedtuple('RSS_row', ('RSSId', 'UserId', 'Url', 'DateRSS'))
    # -------------------------------------------------------

    class _Table:
        def __init__(self, owner, table_name: str, auto_save=True):
            self._table_name = table_name
            self._auto_save = auto_save
            self._owner = owner
            self._connection = owner._connection
            self._cursor = owner._cursor

        def _save_if_possible(self):
            if self._auto_save:
                self._connection.commit()

        def rename(self, new_name: str):
            """
            to rename this table to another name, ERROR will raise if the new_name already exists

            :return: None
            """
            self._cursor.execute(f'ALTER TABLE {self._table_name} RENAME TO {new_name}')
            self._table_name = new_name

        def drop(self):
            """
            to delete a table forever, CAREFUL this process is AUTO-SAVE

            :return: None
            """
            self._cursor.execute(f'DROP TABLE {self._table_name}')

        def duplicate(self, new_name: str):
            """
            create a copy of this table, with new_name

            :param new_name: the name of new table
            :return: the duplicated table as class
            """

            result = None
            if isinstance(self, self._owner._Users):
                self._owner._add_Users_table(new_name)
                result = self._owner.Users(new_name, auto_create=False)
            elif isinstance(self, self._owner._Follows):
                self._owner._add_Follows_table(new_name, self._reference)
                result = self._owner.Follows(new_name, auto_create=False)
            elif isinstance(self, self._owner._Stats):
                self._owner._add_Stats_table(new_name, self._reference)
                result = self._owner.Stats(new_name, auto_create=False)
            elif isinstance(self, self._owner._RSS):
                self._owner._add_RSS_table(new_name, self._reference)
                result = self._owner.RSS(new_name, auto_create=False)
            elif isinstance(self, self._owner._Giveaways):
                self._owner._add_Giveaways_table(new_name, self._reference)
                result = self._owner.Giveaways(new_name, auto_create=False)
            self._cursor.execute(f'INSERT INTO {new_name} SELECT * FROM {self._table_name}')
            self._save_if_possible()
            return result

        def get_table_info(self):
            """
            :return: a dictionary presents some information about this table
            """
            return get_table_info(self._cursor, self._table_name)

    class _Users(_Table):
        def __init__(self, owner, table_name='Users', auto_save=True):
            super().__init__(owner, table_name, auto_save)

        def users_count(self):
            """
            :return: all users count in the table
            """
            self._cursor.execute(f'SELECT COUNT(*) FROM {self._table_name}')
            return self._cursor.fetchone()[0]

        def user_exists(self, IdAccount):
            """
            :param IdAccount: the target user
            :return: True or False
            """
            self._cursor.execute(
                f'SELECT IdAccount FROM {self._table_name} WHERE IdAccount=?',
                (IdAccount,))
            return self._cursor.fetchone() is not None

        def get_users(self, UserId=None, IdAccount=None, NameAccount=None):
            """
            returns a tuple of all matched users with the passed arguments,
            all of the arguments are optimal
            :return: list of named tuple <Users_row>
            """
            params = []
            where = ''
            if UserId is not None:
                params.append(UserId)
                where += 'UserId = ?'
            if IdAccount is not None:
                params.append(IdAccount)
                where += ' AND ' if UserId is not None else ''
                where += 'IdAccount = ?'
            if NameAccount is not None:
                params.append(NameAccount)
                where += ' AND ' if IdAccount is not None or UserId is not None else ''
                where += 'NameAccount = ?'
            params = tuple(params)
            if where != '':
                where = 'WHERE ' + where
            order = f'SELECT * FROM {self._table_name} {where}'
            self._cursor.execute(order, params)
            return [self._owner.Users_row(*x) for x in self._cursor.fetchall()]

        def add_user(self, IdAccount: str, NameAccount: str):
            """
            to add a new user, requires IdAccount and NameAccount, UserId is AUTO-ENCREMENT

            :return: UserId when success, or None
            """
            self._cursor.execute(
                f'INSERT INTO {self._table_name} (IdAccount, NameAccount) VALUES (?, ?)',
                (IdAccount, NameAccount))
            self._save_if_possible()
            self._cursor.execute(
                f'SELECT MAX(UserId) FROM {self._table_name} WHERE IdAccount = ? AND NameAccount = ?',
                (IdAccount, NameAccount))
            return self._cursor.fetchone()[0]

        def update_user(self, UserId: int, new_IdAccount=None, new_NameAccount=None):
            """
            this method allows you to change the IdAccount or NameAccount of a user

            :param UserId: target user
            :param new_IdAccount: new value
            :param new_NameAccount: new value
            :return: None
            """
            if new_IdAccount == new_NameAccount is None:
                return None
            params = []
            set_ = ''
            if new_IdAccount is not None:
                params.append(new_IdAccount)
                set_ += ' IdAccount = ?'
            if new_NameAccount is not None:
                params.append(new_NameAccount)
                set_ += ', ' if new_IdAccount is not None else ''
                set_ += 'NameAccount = ?'
            params.append(UserId)
            params = tuple(params)
            self._cursor.execute(
                f'UPDATE {self._table_name} SET {set_} WHERE UserId = ?',
                params)
            self._save_if_possible()

        def delete_user(self, UserId: int):
            """
            you can specify a user to delete by UserId

            :param UserId: the target user
            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name} WHERE UserId = ?', (UserId,))
            self._save_if_possible()

        def delete_all_users(self):
            """
            CAREFUL this method deletes all the users from the table

            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name}')
            self._save_if_possible()

    class _Follows(_Table):
        def __init__(self, owner, table_name='Follows', reference='Users', auto_save=True):
            super().__init__(owner, table_name, auto_save)
            self._reference = reference

        def follows_count(self):
            """
            :return: all follows count in the table
            """
            self._cursor.execute(f'SELECT COUNT(*) FROM {self._table_name}')
            return self._cursor.fetchone()[0]

        def follow_exists(self, FollowId):
            """
            :param FollowId: target follow
            :return: True or False
            """
            self._cursor.execute(
                f'SELECT FollowId FROM {self._table_name} WHERE FollowId=?',
                (FollowId,))
            return self._cursor.fetchone() is not None

        def get_follows(self, FollowId=None, UserId=None, FollowIdAccount=None, DateFollow=None):
            """
            returns a tuple of all matched follows with the passed arguments,
            all of the arguments are optimal
            :return: list of named tuple <Follows_row>
            """
            params = []
            where = ''
            if FollowId is not None:
                params.append(FollowId)
                where += 'FollowId = ?'
            if UserId is not None:
                params.append(UserId)
                where += ' AND ' if FollowId is not None else ''
                where += 'UserId = ?'
            if FollowIdAccount is not None:
                params.append(FollowIdAccount)
                where += ' AND ' if UserId is not None or FollowId is not None else ''
                where += 'FollowIdAccount = ?'
            if DateFollow is not None:
                params.append(DateFollow)
                where += ' AND ' if FollowIdAccount is not None or UserId is not None or FollowId is not None else ''
                where += 'DateFollow = ?'
            params = tuple(params)
            if where != '':
                where = 'WHERE ' + where
            order = f'SELECT * FROM {self._table_name} {where}'
            self._cursor.execute(order, params)
            return [self._owner.Follows_row(*x) for x in self._cursor.fetchall()]

        def add_follow(self, UserId: int, FollowIdAccount: str, DateFollow: str):
            """
            to add a new follow, requires UserId and FollowIdAccount and DateFollow, FollowId is AUTO-ENCREMENT

            :return: FollowId when success, or None
            """
            self._cursor.execute(
                f'INSERT INTO {self._table_name} (UserId, FollowIdAccount, DateFollow) VALUES (?, ?, ?)',
                (UserId, FollowIdAccount, DateFollow))
            self._save_if_possible()
            # > the next line just to get the ID of the last inserted row, which is this one
            self._cursor.execute(
                f'SELECT MAX(FollowId) FROM {self._table_name} WHERE UserId = ? AND FollowIdAccount = ? And DateFollow = ?',
                (UserId, FollowIdAccount, DateFollow))
            return self._cursor.fetchone()[0]

        def update_follow(self, FollowId: int, new_UserId=None, new_FollowIdAccount=None, new_DateFollow=None):
            """
            this method allows you to change the values of a follow

            :param FollowId: target follow
            :param new_UserId: new value
            :param new_FollowIdAccount: new value
            :param new_DateFollow: new value
            :return: None
            """
            if new_UserId == new_FollowIdAccount == new_DateFollow is None:
                return None
            params = []
            set_ = ''
            if new_UserId is not None:
                params.append(new_UserId)
                set_ += ' UserId = ?'
            if new_FollowIdAccount is not None:
                params.append(new_FollowIdAccount)
                set_ += ', ' if new_UserId is not None else ''
                set_ += ' FollowIdAccount = ?'
            if new_DateFollow is not None:
                params.append(new_DateFollow)
                set_ += ', ' if new_FollowIdAccount is not None or new_UserId is not None else ''
                set_ += ' DateFollow = ?'
            params.append(FollowId)
            params = tuple(params)
            self._cursor.execute(
                f'UPDATE {self._table_name} SET {set_} WHERE FollowId = ?',
                params)
            self._save_if_possible()

        def delete_follow(self, FollowId: int):
            """
            you can specify a follow to delete by FollowId

            :param FollowId: the target follow
            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name} WHERE FollowId = ?', (FollowId,))
            self._save_if_possible()

        def delete_all_follows(self):
            """
            CAREFUL this method deletes all of the follows from the table

            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name}')
            self._save_if_possible()

        def get_follow_referenced_user(self, FollowId: int):
            """
            :param FollowId: target follow
            :return: an <Users_row> presents the user in the referenced or parent table
            """
            self._cursor.execute(f'SELECT UserId FROM {self._table_name} WHERE FollowId = ?', (FollowId,))
            uid = self._cursor.fetchone()[0]
            self._cursor.execute(f'SELECT * FROM {self._reference} WHERE UserId = ?', (uid,))
            return self._cursor.fetchone()

    class _Stats(_Table):
        def __init__(self, owner, table_name='Stats', reference='Users', auto_save=True):
            super().__init__(owner, table_name, auto_save)
            self._reference = reference

        def stats_count(self):
            """
            :return: all stats count in the table
            """
            self._cursor.execute(f'SELECT COUNT(*) FROM {self._table_name}')
            return self._cursor.fetchone()[0]

        def stat_exists(self, StatId):
            """
            :param StatId: target stat
            :return: True or False
            """
            self._cursor.execute(
                f'SELECT StatId FROM {self._table_name} WHERE StatId=?',
                (StatId,))
            return self._cursor.fetchone() is not None

        def get_stats(self, StatId=None, UserId=None, NbRetweet=None, NbTag=None):
            """
            returns a tuple of all matched stats with the passed arguments,
            all of the arguments are optimal
            :return: list of named tuple <Stats_row>
            """
            params = []
            where = ''
            if StatId is not None:
                params.append(StatId)
                where += 'StatId = ?'
            if UserId is not None:
                params.append(UserId)
                where += ' AND ' if StatId is not None else ''
                where += 'UserId = ?'
            if NbRetweet is not None:
                params.append(NbRetweet)
                where += ' AND ' if UserId is not None or StatId is not None else ''
                where += 'NbRetweet = ?'
            if NbTag is not None:
                params.append(NbTag)
                where += ' AND ' if NbRetweet is not None or UserId is not None or StatId is not None else ''
                where += 'NbTag = ?'
            params = tuple(params)
            if where != '':
                where = 'WHERE ' + where
            order = f'SELECT * FROM {self._table_name} {where}'
            self._cursor.execute(order, params)
            return [self._owner.Stats_row(*x) for x in self._cursor.fetchall()]

        def add_stat(self, UserId: int, NbRetweet: str, NbTag: str):
            """
            to add a new stat, requires UserId and NbRetweet and NbTag, StatId is AUTO-ENCREMENT

            :return: StatId when success, or None
            """
            self._cursor.execute(
                f'INSERT INTO {self._table_name} (UserId, NbRetweet, NbTag) VALUES (?, ?, ?)',
                (UserId, NbRetweet, NbTag))
            self._save_if_possible()
            # > the next line just to get the ID of the last inserted row, which is this one
            self._cursor.execute(
                f'SELECT MAX(StatId) FROM {self._table_name} WHERE UserId = ? AND NbRetweet = ? And NbTag = ?',
                (UserId, NbRetweet, NbTag))
            return self._cursor.fetchone()[0]

        def update_stat(self, StatId: int, new_UserId=None, new_NbRetweet=None, new_NbTab=None):
            """
            this method allows you to change the values of a stat

            :param StatId: target stat
            :param new_UserId: new value
            :param new_NbRetweet: new value
            :param new_NbTab: new value
            :return: None
            """
            if new_UserId == new_NbRetweet == new_NbTab is None:
                return None
            params = []
            set_ = ''
            if new_UserId is not None:
                params.append(new_UserId)
                set_ += ' UserId = ?'
            if new_NbRetweet is not None:
                params.append(new_NbRetweet)
                set_ += ', ' if new_UserId is not None else ''
                set_ += ' NbRetweet = ?'
            if new_NbTab is not None:
                params.append(new_NbTab)
                set_ += ', ' if new_NbRetweet is not None or new_UserId is not None else ''
                set_ += ' NbTag = ?'
            params.append(StatId)
            params = tuple(params)
            self._cursor.execute(
                f'UPDATE {self._table_name} SET {set_} WHERE StatId = ?',
                params)
            self._save_if_possible()

        def delete_stat(self, StatId: int):
            """
            you can specify a stat to delete by StatId

            :param StatId: the target stat
            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name} WHERE StatId = ?', (StatId,))
            self._save_if_possible()

        def delete_all_stats(self):
            """
            CAREFUL this method deletes all of the stats from the table

            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name}')
            self._save_if_possible()

        def get_stat_referenced_user(self, StatId: int):
            """
            :param StatId: target stat
            :return: an <Stats_row> presents the user in the referenced or parent table
            """
            self._cursor.execute(f'SELECT UserId FROM {self._table_name} WHERE StatId = ?', (StatId,))
            uid = self._cursor.fetchone()[0]
            self._cursor.execute(f'SELECT * FROM {self._reference} WHERE UserId = ?', (uid,))
            return self._cursor.fetchone()

    class _RSS(_Table):
        def __init__(self, owner, table_name='RSS', reference='Users', auto_save=True):
            super().__init__(owner, table_name, auto_save)
            self._reference = reference

        def rss_count(self):
            """
            :return: all rss count in the table
            """
            self._cursor.execute(f'SELECT COUNT(*) FROM {self._table_name}')
            return self._cursor.fetchone()[0]

        def rss_exists(self, Url):
            """
            :param Url: target Url
            :return: True or False
            """
            self._cursor.execute(
                f'SELECT RSSId FROM {self._table_name} WHERE Url=?',
                (Url,))
            return self._cursor.fetchone() is not None

        def get_rss(self, RSSId=None, UserId=None, Url=None, DateRSS=None):
            """
            returns a tuple of all matched RSS with the passed arguments,
            all of the arguments are optimal
            :return: list of named tuple <RSS_row>
            """
            params = []
            where = ''
            if RSSId is not None:
                params.append(RSSId)
                where += 'RSSId = ?'
            if UserId is not None:
                params.append(UserId)
                where += ' AND ' if RSSId is not None else ''
                where += 'UserId = ?'
            if Url is not None:
                params.append(Url)
                where += ' AND ' if UserId is not None or RSSId is not None else ''
                where += 'Url = ?'
            if DateRSS is not None:
                params.append(DateRSS)
                where += ' AND ' if Url is not None or UserId is not None or RSSId is not None else ''
                where += 'DateRSS = ?'
            params = tuple(params)
            if where != '':
                where = 'WHERE ' + where
            order = f'SELECT * FROM {self._table_name} {where}'
            self._cursor.execute(order, params)
            return [self._owner.RSS_row(*x) for x in self._cursor.fetchall()]

        def add_rss(self, UserId: int, Url: str, DateRSS: str):
            """
            to add a new RSS, requires UserId and Url and DateRSS, RSSId is AUTO-ENCREMENT

            :return: RSSId when success, or None
            """
            self._cursor.execute(
                f'INSERT INTO {self._table_name} (UserId, Url, DateRSS) VALUES (?, ?, ?)',
                (UserId, Url, DateRSS))
            self._save_if_possible()
            # > the next line just to get the ID of the last inserted row, which is this one
            self._cursor.execute(
                f'SELECT MAX(RSSId) FROM {self._table_name} WHERE UserId = ? AND Url = ? And DateRSS = ?',
                (UserId, Url, DateRSS))
            return self._cursor.fetchone()[0]

        def update_rss(self, RSSId: int, new_UserId=None, new_Url=None, new_DateRSS=None):
            """
            this method allows you to change the values of a RSS

            :param RSSId: target RSS
            :param new_UserId: new value
            :param new_Url: new value
            :param new_DateRSS: new value
            :return: None
            """
            if new_UserId == new_Url == new_DateRSS is None:
                return None
            params = []
            set_ = ''
            if new_UserId is not None:
                params.append(new_UserId)
                set_ += ' UserId = ?'
            if new_Url is not None:
                params.append(new_Url)
                set_ += ', ' if new_UserId is not None else ''
                set_ += ' Url = ?'
            if new_DateRSS is not None:
                params.append(new_DateRSS)
                set_ += ', ' if new_Url is not None or new_UserId is not None else ''
                set_ += ' DateRSS = ?'
            params.append(RSSId)
            params = tuple(params)
            self._cursor.execute(
                f'UPDATE {self._table_name} SET {set_} WHERE RSSId = ?',
                params)
            self._save_if_possible()

        def delete_rss(self, RSSId: int):
            """
            you can specify an RSS to delete by RSSId

            :param RSSId: the target RSS
            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name} WHERE RSSId = ?', (RSSId,))
            self._save_if_possible()

        def delete_all_rss(self):
            """
            CAREFUL this method deletes all of the RSS from the table

            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name}')
            self._save_if_possible()

        def get_stat_referenced_user(self, RSSId: int):
            """
            :param RSSId: target RSS
            :return: an <RSS_row> presents the user in the referenced or parent table
            """
            self._cursor.execute(f'SELECT UserId FROM {self._table_name} WHERE RSSId = ?', (RSSId,))
            uid = self._cursor.fetchone()[0]
            self._cursor.execute(f'SELECT * FROM {self._reference} WHERE UserId = ?', (uid,))
            return self._cursor.fetchone()

    class _Giveaways(_Table):
        def __init__(self, owner, table_name='Giveaways', reference='Users', auto_save=True):
            super().__init__(owner, table_name, auto_save)
            self._reference = reference

        def giveaways_count(self):
            """
            :return: all Giveaways count in the table
            """
            self._cursor.execute(f'SELECT COUNT(*) FROM {self._table_name}')
            return self._cursor.fetchone()[0]

        def giveaway_exists(self, GiveawayId):
            """
            :param GiveawayId: target Giveaway
            :return: True or False
            """
            self._cursor.execute(
                f'SELECT GiveawayId FROM {self._table_name} WHERE GiveawayId=?',
                (GiveawayId,))
            return self._cursor.fetchone() is not None

        def get_giveaways(self, GiveawayId=None, UserId=None,
                    GiveawayUserId=None, GiveawayUsername=None, TweetId=None, TweetMessage=None,
                    NeedTags=None, NeedRt=None, NeedComment=None, NeedLike=None, NeedFollow=None,
                    DateBot=None, TagsBot=None, RtBot=None, FollowBot=None, LikeBot=None, CommentBot=None, PrivateMessage=None ):
            """
            returns a tuple of all matched Giveaways with the passed arguments,
            all of the arguments are optimal
            :return: list of named tuple <Giveaways_row>
            """
            params = []
            where = ''
            if GiveawayId is not None:
                params.append(GiveawayId)
                where += 'GiveawayId = ?'
            if UserId is not None:
                params.append(UserId)
                where += ' AND ' if where else ''
                where += 'UserId = ?'
            if GiveawayUserId is not None:
                params.append(GiveawayUserId)
                where += ' AND ' if where else ''
                where += 'GiveawayUserId = ?'
            if GiveawayUsername is not None:
                params.append(GiveawayUsername)
                where += ' AND ' if where else ''
                where += 'GiveawayUsername = ?'
            if TweetId is not None:
                params.append(TweetId)
                where += ' AND ' if where else ''
                where += 'TweetId = ?'
            if TweetMessage is not None:
                params.append(TweetMessage)
                where += ' AND ' if where else ''
                where += 'TweetMessage = ?'
            if NeedTags is not None:
                params.append(NeedTags)
                where += ' AND ' if where else ''
                where += 'NeedTags = ?'
            if NeedRt is not None:
                params.append(NeedRt)
                where += ' AND ' if where else ''
                where += 'NeedRt = ?'
            if NeedComment is not None:
                params.append(NeedComment)
                where += ' AND ' if where else ''
                where += 'NeedComment = ?'
            if NeedLike is not None:
                params.append(NeedLike)
                where += ' AND ' if where else ''
                where += 'NeedLike = ?'
            if NeedFollow is not None:
                params.append(NeedFollow)
                where += ' AND ' if where else ''
                where += 'NeedFollow = ?'
            if DateBot is not None:
                params.append(DateBot)
                where += ' AND ' if where else ''
                where += 'DateBot = ?'
            if TagsBot is not None:
                params.append(TagsBot)
                where += ' AND ' if where else ''
                where += 'TagsBot = ?'
            if RtBot is not None:
                params.append(RtBot)
                where += ' AND ' if where else ''
                where += 'RtBot = ?'
            if FollowBot is not None:
                params.append(FollowBot)
                where += ' AND ' if where else ''
                where += 'FollowBot = ?'
            if LikeBot is not None:
                params.append(LikeBot)
                where += ' AND ' if where else ''
                where += 'LikeBot = ?'
            if CommentBot is not None:
                params.append(CommentBot)
                where += ' AND ' if where else ''
                where += 'CommentBot = ?'
            if PrivateMessage is not None:
                params.append(PrivateMessage)
                where += ' AND ' if where else ''
                where += 'PrivateMessage = ?'
            params = tuple(params)
            if where != '':
                where = 'WHERE ' + where
            order = f'SELECT * FROM {self._table_name} {where} ORDER BY DateBot DESC'
            self._cursor.execute(order, params)

            return [self._owner.Giveaways_row(*x) for x in self._cursor.fetchall()]

        def add_giveaway(self, UserId='', GiveawayUserId='', GiveawayUsername='', TweetId='', TweetMessage='', NeedTags='', NeedRt='', 
                NeedComment='', NeedLike='', NeedFollow='',  DateBot='', TagsBot='', RtBot='', FollowBot='', LikeBot='', CommentBot='', PrivateMessage=''):
            """
            Add a new Giveaway

            :param UserId Integer/Boolean : User account id
            :param GiveawayUserId Integer/Boolean : User account id of the creator of the giveaway
            :param GiveawayUsername String : User account name of the creator of the giveaway
            :param TweetId Integer/Boolean : Tweet/Giveaway id
            :param TweetMessage String : Tweet/Giveaway message text
            :param NeedTags Integer/Boolean : Giveaway ask for Tags other users
            :param NeedRt Integer/Boolean : Giveaway ask for RT action
            :param NeedComment Integer/Boolean : Giveaway ask for Comment
            :param NeedLike Integer/Boolean : Giveaway ask for Like
            :param NeedFollow Integer/Boolean :  Giveaway ask for Follows
            :param DateBot Integer/Boolean : Date of participation to the giveaway
            :param TagsBot Integer/Boolean : Bot have tags users on this giveaway
            :param RtBot Integer/Boolean :  Bot have RT this giveaway
            :param FollowBot Integer/Boolean :  Bot have Follow the author of this giveaway
            :param LikeBot Integer/Boolean :  Bot have Like this giveaway
            :param CommentBot Integer/Boolean :  Bot have comment users on this giveaway
            :param PrivateMessage Integer/Boolean : Bot user have been contact  by the author of the giveaway after participation

            :return: GiveawayId when success, or None
            """
            self._cursor.execute(
                f'INSERT INTO {self._table_name} (UserId, GiveawayUserId, GiveawayUsername, TweetId, TweetMessage, NeedTags, NeedRt, NeedComment, NeedLike, NeedFollow,  DateBot, TagsBot, RtBot, FollowBot, LikeBot, CommentBot, PrivateMessage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (UserId, GiveawayUserId, GiveawayUsername, TweetId, TweetMessage, NeedTags, NeedRt, NeedComment, NeedLike, NeedFollow,  DateBot, TagsBot, RtBot, FollowBot, LikeBot, CommentBot, PrivateMessage
))
            self._save_if_possible()
            # > the next line just to get the ID of the last inserted row, which is this one
            self._cursor.execute(f'SELECT MAX(GiveawayId) FROM {self._table_name}')
            return self._cursor.fetchone()[0]

        def update_giveaway(self, GiveawayId: int, new_UserId=None, new_GiveawayUserId=None, new_GiveawayUsername=None, 
                new_TweetId=None, new_TweetMessage=None, new_NeedTags=None, new_NeedRt=None, new_NeedComment=None, new_NeedLike=None, new_NeedFol1low=None,  new_DateBot=None, new_TagsBot=None, new_RtBot=None, new_FollowBot=None, new_LikeBot=None, new_CommentBot=None, new_PrivateMessage=None):
            """
            this method allows you to change the values of a Giveaway

            :param GiveawayId: target Giveaway
            :param UserId : new value
            :param GiveawayUserId : new value
            :param GiveawayUsername : new value
            :param TweetId : new value
            :param TweetMessage : new value
            :param NeedTags : new value
            :param NeedRt : new value
            :param NeedComment : new value
            :param NeedLike : new value
            :param NeedFollow : new value
            :param DateBot : new value
            :param TagsBot : new value
            :param RtBot : new value
            :param FollowBot : new value
            :param LikeBot : new value
            :param CommentBot : new value
            :param PrivateMessage : new value

            :return: None
            """
            if GiveawayId is None:
                return None
            params = []
            set_ = ''
            if new_UserId is not None:
                params.append(new_UserId)
                set_ += ' UserId = ?'
            if new_GiveawayUserId is not None:
                params.append(new_GiveawayUserId)
                set_ += ', ' if set_ else ''
                set_ += ' GiveawayUserId = ?'
            if new_GiveawayUsername is not None:
                params.append(new_GiveawayUsername)
                set_ += ', ' if set_ else ''
                set_ += ' GiveawayUsername = ?'
            if new_TweetId is not None:
                params.append(new_TweetId)
                set_ += ', ' if set_ else ''
                set_ += ' TweetId = ?'
            if new_TweetMessage is not None:
                params.append(new_TweetMessage)
                set_ += ', ' if set_ else ''
                set_ += ' TweetMessage = ?'
            if new_NeedTags is not None:
                params.append(new_NeedTags)
                set_ += ', ' if set_ else ''
                set_ += ' NeedTags = ?'
            if new_NeedRt is not None:
                params.append(new_NeedRt)
                set_ += ', ' if set_ else ''
                set_ += ' NeedRt = ?'
            if new_NeedComment is not None:
                params.append(new_NeedComment)
                set_ += ', ' if set_ else ''
                set_ += ' NeedComment = ?'
            if new_NeedLike is not None:
                params.append(new_NeedLike)
                set_ += ', ' if set_ else ''
                set_ += ' NeedLike = ?'
            if new_NeedFol1low is not None:
                params.append(new_NeedFol1low)
                set_ += ', ' if set_ else ''
                set_ += ' NeedFol1low = ?'
            if new_DateBot is not None:
                params.append(new_DateBot)
                set_ += ', ' if set_ else ''
                set_ += ' DateBot = ?'
            if new_TagsBot is not None:
                params.append(new_TagsBot)
                set_ += ', ' if set_ else ''
                set_ += ' TagsBot = ?'
            if new_RtBot is not None:
                params.append(new_RtBot)
                set_ += ', ' if set_ else ''
                set_ += ' RtBot = ?'
            if new_FollowBot is not None:
                params.append(new_FollowBot)
                set_ += ', ' if set_ else ''
                set_ += ' FollowBot = ?'
            if new_LikeBot is not None:
                params.append(new_LikeBot)
                set_ += ', ' if set_ else ''
                set_ += ' LikeBot = ?'
            if new_CommentBot is not None:
                params.append(new_CommentBot)
                set_ += ', ' if set_ else ''
                set_ += ' CommentBot = ?'
            if new_PrivateMessage is not None:
                params.append(new_PrivateMessage)
                set_ += ', ' if set_ else ''
                set_ += ' PrivateMessage = ?'
            params.append(GiveawayId)
            params = tuple(params)
            self._cursor.execute(
                f'UPDATE {self._table_name} SET {set_} WHERE GiveawayId = ?',
                params)
            self._save_if_possible()

        def delete_Giveaway(self, GiveawayId: int):
            """
            you can specify a Giveaway to delete by GiveawayId

            :param GiveawayId: the target Giveaway
            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name} WHERE GiveawayId = ?', (GiveawayId,))
            self._save_if_possible()

        def delete_all_Giveaways(self):
            """
            CAREFUL this method deletes all of the Giveaways from the table

            :return: None
            """
            self._cursor.execute(f'DELETE FROM {self._table_name}')
            self._save_if_possible()

        def get_Giveaway_referenced_user(self, GiveawayId: int):
            """
            :param GiveawayId: target Giveaway
            :return: an <Giveaways_row> presents the user in the referenced or parent table
            """
            self._cursor.execute(f'SELECT UserId FROM {self._table_name} WHERE GiveawayId = ?', (GiveawayId,))
            uid = self._cursor.fetchone()[0]
            self._cursor.execute(f'SELECT * FROM {self._reference} WHERE UserId = ?', (uid,))
            return self._cursor.fetchone()
    # ------------------------------------------------------

    def __init__(self, database_file: str):
        """
        sets the connection to the database_file, if not exists, it will create one

        :param database_file: the path of the database file
        """
        self._connection = sqlite3.connect(database_file)
        self._cursor = self._connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _add_Users_table(self, a_name: str, if_not_exists=False):
        """
        This method creates a Users table with a chosen name

        :param a_name: the chosen name
        :param if_not_exists: set to True to avoid error if already exists
        :return: None
        """
        ine = 'IF NOT EXISTS' if if_not_exists else ''
        self._cursor.execute(f'CREATE TABLE {ine} {a_name} ('
                            f'UserId INTEGER PRIMARY KEY AUTOINCREMENT,'
                            f'IdAccount TEXT,'
                            f'NameAccount TEXT'
                            f')')

    def _add_Follows_table(self, a_name: str, references: str, if_not_exists=False):
        """
        This method creates a Follows table with a chosen name

        :param a_name: the chosen name
        :param if_not_exists: set to True to avoid error if already exists
        :return: None
        """
        ine = 'IF NOT EXISTS' if if_not_exists else ''
        self._cursor.execute(f'CREATE TABLE {ine} {a_name} ('
                            f'FollowId INTEGER PRIMARY KEY AUTOINCREMENT,'
                            f'UserId INTEGER REFERENCES {references}(UserId),'
                            f'FollowIdAccount TEXT,'
                            f'DateFollow DATE'
                            f')')

    def _add_Stats_table(self, a_name: str, references: str, if_not_exists=False):
        """
        This method creates a Stats table with a chosen name

        :param a_name: the chosen name
        :param if_not_exists: set to True to avoid error if already exists
        :return: None
        """
        ine = 'IF NOT EXISTS' if if_not_exists else ''
        self._cursor.execute(f'CREATE TABLE {ine} {a_name} ('
                            f'StatId INTEGER PRIMARY KEY AUTOINCREMENT,'
                            f'UserId INTEGER REFERENCES {references}(UserId),'
                            f'NbRetweet INTEGER,'
                            f'NbTag INTEGER'
                            f')')

    def _add_RSS_table(self, a_name: str, references: str, if_not_exists=False):
        """
        This method creates a RSS table with a chosen name

        :param a_name: the chosen name
        :param if_not_exists: set to True to avoid error if already exists
        :return: None
        """
        ine = 'IF NOT EXISTS' if if_not_exists else ''
        self._cursor.execute(f'CREATE TABLE {ine} {a_name} ('
                            f'RSSId INTEGER PRIMARY KEY AUTOINCREMENT,'
                            f'UserId REFERENCES {references}(UserId),'
                            f'Url TEXT,'
                            f'DateRSS DATE'
                            f')')


    def _add_giveaways_table(self, a_name: str, references: str, if_not_exists=False):
        """
        This method creates a Giveaways table with a chosen name

        :param a_name: the chosen name
        :param if_not_exists: set to True to avoid error if already exists
        :return: None
        """
        ine = 'IF NOT EXISTS' if if_not_exists else ''
        self._cursor.execute(f'CREATE TABLE {ine} {a_name} ('
                            f'GiveawayId INTEGER PRIMARY KEY AUTOINCREMENT,'
                            f'UserId INTEGER REFERENCES {references}(UserId),'
                            f'GiveawayUserId INTEGER,'
                            f'GiveawayUsername TEXT,'
                            f'TweetId INTEGER,'
                            f'TweetMessage TEXT,'
                            f'NeedTags INTEGER,'
                            f'NeedComment INTEGER,'
                            f'NeedLike INTEGER,'
                            f'NeedFollow INTEGER,'
                            f'NeedRT INTEGER,'
                            f'DateBot DATE,'
                            f'TagsBot INTEGER,'
                            f'RtBot INTEGER,'
                            f'FollowBot INTEGER,'
                            f'LikeBot INTEGER,'
                            f'CommentBot INTEGER,'
                            f'PrivateMessage INTEGER'
                            f')')
    # Check State Methods

    def table_exists(self, table_name: str):
        """
        checks if a table exists or not using the name

        :param table_name: the name of the target table
        :return: True or False
        """
        return get_table_info(self._cursor, table_name) is not None

    def tables_count(self):
        self._cursor.execute(f'SELECT COUNT(*) FROM {MASTER}')
        return self._cursor.fetchone()[0]

    def get_all_tables(self):
        """
        :return: a tuple presents the names of all the tables in the database
        """
        self._cursor.execute(f'SELECT name FROM {MASTER}')
        return tuple(self._cursor.fetchall())

    def save_changes(self):
        """
        any changes on rows of a table needs to be save
        :return: none
        """
        self._connection.commit()

    def Users(self, table_name='Users', auto_create=True, auto_save=True):
        """
        control a Users table with this method

        :param table_name: the name of the table, default to "Users"
        :param auto_create: to create the table if doesn't exists, to avoid error
        :param auto_save: to save changes automatically, highly recommended
        :return: <_Users> instance
        """
        if auto_create:
            self._add_Users_table(table_name, True)
        return self._Users(self, table_name, auto_save)

    def Follows(self, table_name='Follows', reference_table='Users', auto_create=True, auto_save=True):
        """
        control a Follows table with this method

        :param table_name: the name of the table, default to "Follows"
        :param reference_table: the reference table to refer UserId column
        :param auto_create: to create the table if doesn't exists, to avoid error
        :param auto_save: to save changes automatically, highly recommended
        :return: <_Follow> instance
        """
        if auto_create:
            self._add_Follows_table(table_name, reference_table, True)
        return self._Follows(self, table_name, reference_table, auto_save)

    def Stats(self, table_name='Stats', reference_table='Users', auto_create=True, auto_save=True):
        """
        control a Stats table with this method

        :param table_name: the name of the table, default to "Stats"
        :param reference_table: the reference table to refer UserId column
        :param auto_create: to create the table if doesn't exists, to avoid error
        :param auto_save: to save changes automatically, highly recommended
        :return: <_Stats> instance
        """
        if auto_create:
            self._add_Stats_table(table_name, reference_table, True)
        return self._Stats(self, table_name, reference_table, auto_save)

    def Giveaways(self, table_name='Giveaways', reference_table='Users', auto_create=True, auto_save=True):
        """
        control a Giveaways table with this method

        :param table_name: the name of the table, default to "Giveaways"
        :param reference_table: the reference table to refer UserId column
        :param auto_create: to create the table if doesn't exists, to avoid error
        :param auto_save: to save changes automatically, highly recommended
        :return: <_Giveaways> instance
        """
        if auto_create:
            self._add_giveaways_table(table_name, reference_table, True)
        return self._Giveaways(self, table_name, reference_table, auto_save)

    def RSS(self, table_name='RSS', reference_table='Users', auto_create=True, auto_save=True):
        """
        control an RSS table with this method

        :param table_name: the name of the table, default to "RSS"
        :param reference_table: the reference table to refer UserId column
        :param auto_create: to create the table if doesn't exists, to avoid error
        :param auto_save: to save changes automatically, highly recommended
        :return: <_RSS> instance
        """
        if auto_create:
            self._add_RSS_table(table_name, reference_table, True)
        return self._RSS(self, table_name, reference_table, auto_save)

    def close(self):
        self._connection.close()
