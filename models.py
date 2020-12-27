#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml

from time import mktime, strftime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean


Base = declarative_base()

from datetime import datetime

def db_connect(account):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    db_path = 'databases/rss_{}.db'.format(account)
    return create_engine("sqlite:///{}".format(db_path))

def create_tables(account):
    """"""
    engine = db_connect(account)
    Base.metadata.create_all(engine)

class FeedSet:
    """
    feeds.yml item wrapper
    """
    def __init__(self, data):
        if(isinstance(data, dict)):
            self.data = data

    @property
    def twitter_keys(self):
        return self.data['twitter']

    @property
    def urls(self):
        return self.data['urls']

class RSSContent(Base):
    __tablename__ = 'rsscontent'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    title = Column(String)
    dateAdded = Column(DateTime, default=datetime.now())
    published = Column(Boolean, unique=False, default=False)

    def __repr__(self):
       return "<RSSContent(dateAdded='{}', title='{}', url='{}', published='{}')>".format(self.dateAdded, self.title, self.url, self.published)

    def __init__(self, url, title, dateAdded=None, published=False):
        self.url = url
        self.title = title
        self.dateAdded = dateAdded
        self.published = published
