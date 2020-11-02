import json
import io
from datetime import datetime
import tkinter

filepath = 'E:/Work/tweet.js'


def convert_js_file(filepath):
    with io.open(filepath, encoding='utf8') as js_file:
        data = js_file.read()
        objs = data[data.find('[') : data.rfind(']')+1]
        tweets_dict = json.loads(objs)

    return tweets_dict


def convert_datetime(tweets_dict):
    for tweet in tweets_dict:
        tweet['tweet']['created_at'] = datetime.strptime(tweet['tweet']['created_at'], '%a %b %d %H:%M:%S %z %Y')

    return tweets_dict


tweets = convert_js_file(filepath)
tweets = convert_datetime(tweets)
