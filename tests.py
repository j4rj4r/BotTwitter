import unittest
from models import FeedSet, Base, RSSContent
import config
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
from test_data.feedparser_data import fake_response
from helpers import RSSContentHelper, FeedSetHelper

class TestFeedSet(unittest.TestCase):
    def setUp(self):
        url = config.DB_TEST_URL
        if not url:
            self.skipTest("No database URL set")
        engine = sqlalchemy.create_engine(url)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    

    feedparser_fake_response = fake_response

    def feed_data_dict(self):
        data = {
            'urls': ['https://news.ycombinator.com/rss'],
            'hashtags': '#example',
            'twitter': {
                'consumer_key': 'XXXXXXXXXXX',
                'access_secret': 'XXXXXXXXXXXXXX',
                'consumer_secret': 'XXXXXXXXXXXXXX',
                'access_key': 'XXXXXXXXXXXX'
            },
            'name': 'SimpleItRocks'
        }
        return data

    

    def test_get_twitter_credentials(self):
        data = self.feed_data_dict()
        feed = FeedSet(data)
        keys = feed.twitter_keys

        self.assertIsInstance(keys, dict)
        self.assertIn('consumer_key', keys)
        self.assertIn('access_key', keys)
        self.assertIn('consumer_secret', keys)
        self.assertIn('access_secret', keys)

    def test_urls(self):
        data = self.feed_data_dict()
        feed = FeedSet(data)
        urls = feed.urls

        self.assertIsInstance(urls, list)

    
    @unittest.mock.patch('feedparser.parse', return_value=feedparser_fake_response)
    def test_save_new_pages(self, feedparser_fake_response):

        self.assertEqual(len(self.session.query(RSSContent).all()), 0)
        helper = FeedSetHelper(self.session, self.feed_data_dict())
        helper.get_pages_from_feeds()
        self.assertNotEqual(len(self.session.query(RSSContent).all()), 0)

    @unittest.mock.patch('feedparser.parse', return_value=feedparser_fake_response)        
    def test_not_save_existing_pages(self, feedparser_fake_response):
        # presave an item that is present in the retrieved feed, to check if it
        # has not been saved after downloading new feeds
        entry = fake_response.entries[0]
        items_count = len(fake_response.entries)
        rsscontent = RSSContent(title=entry.title, url=entry.link)
        self.session.add(rsscontent)
        self.assertEqual(len(self.session.query(RSSContent).all()), 1)
        helper = FeedSetHelper(self.session, self.feed_data_dict())

        helper.get_pages_from_feeds()

        self.assertEqual(len(self.session.query(RSSContent).all()), items_count, "Entries count has changed")

if __name__ == '__main__':
    unittest.main()
