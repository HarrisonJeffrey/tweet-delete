import json
import io
import pandas as pd
import tweepy

filepath = 'E:/Work/tweet.js'


def convert_js_file(filepath):
    with io.open(filepath, encoding='utf8') as js_file:
        data = js_file.read()
        objs = data[data.find('['): data.rfind(']')+1]
        tweets_dict = json.loads(objs)

    tweets_dict = [tweet['tweet'] for tweet in tweets_dict]
    tweets = pd.DataFrame(tweets_dict)
    tweets['created_at'] = pd.to_datetime(tweets['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets = tweets.set_index('created_at')

    return tweets.sort_values(by='created_at')


tweets = convert_js_file(filepath)
print(tweets)