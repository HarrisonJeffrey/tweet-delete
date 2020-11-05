import json
import io
from datetime import datetime
import tweepy

filepath = 'E:/Work/tweet.js'


class Tweets:
    def __init__(self, tweets_file):
        self.tweets = self.convert_js_file(tweets_file)

    def convert_datetime(self, tweets_dict):
        for tweet in tweets_dict:
            tweet['tweet']['created_at'] = datetime.strptime(tweet['tweet']['created_at'], '%a %b %d %H:%M:%S %z %Y')

        return tweets_dict

    def convert_js_file(self, filepath):
        with io.open(filepath, encoding='utf8') as js_file:
            data = js_file.read()
            objs = data[data.find('['): data.rfind(']')+1]
            tweets_dict = json.loads(objs)

        tweets_dict = self.convert_datetime(tweets_dict)

        return tweets_dict

    def get_tweet(self, start, end=None):
        if end:
            return self.tweets[start: end]
        else:
            return self.tweets[start]

    def get_tweet_by_id(self, id):
        pass

    def get_tweets_timeframe(self, start, end):
        pass


tweets = Tweets(filepath)
print(tweets.get_tweet(0))