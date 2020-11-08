import json
import io
from pathlib import Path
import pandas as pd
import tweepy

filepath = 'E:/Work/tweet.js'
token_filepath = Path('consumer_token.txt')

access_token = ''
access_token_secret = ''

if token_filepath.exists():
    with open(token_filepath, 'w') as f:
        consumer_key = f.readline().strip()
        consumer_secret = f.readline().strip()
else:
    consumer_key = None
    consumer_secret = None

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def convert_js_file(filepath):
    with io.open(filepath, encoding='utf8') as js_file:
        data = js_file.read()
        objs = data[data.find('['): data.rfind(']')+1]
        tweets_dict = json.loads(objs)

    tweets_dict = [tweet['tweet'] for tweet in tweets_dict]
    tweets = pd.DataFrame(tweets_dict)
    tweets['created_at'] = pd.to_datetime(tweets['created_at'], format='%a %b %d %H:%M:%S %z %Y')

    return tweets.sort_values(by='created_at')


def get_tweets_by_date(tweets, start=None, end=None):
    if start and end:
        return tweets[(tweets['created_at'] >= start) & (tweets['created_at'] <= end)]
    elif start:
        return tweets[tweets['created_at'] >= start]
    elif end:
        return tweets[tweets['created_at'] <= end]


tweets = convert_js_file(filepath)