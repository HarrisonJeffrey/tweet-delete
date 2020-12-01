from decouple import config
import io
import json
from pathlib import Path
import pandas as pd
import tweepy

filepath = 'tweet.js'
token_filepath = Path('.env')

access_token = config('access_token')
access_token_secret = config('access_token_secret')

if token_filepath.exists():
    consumer_key = config('consumer_key')
    consumer_secret = config('consumer_secret')
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
print(tweets.iloc[0])