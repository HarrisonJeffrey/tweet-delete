import io
import json
import pandas as pd


def convert_js_file(filepath):
    with io.open(filepath, encoding='utf8') as js_file:
        data = js_file.read()
        objs = data[data.find('['): data.rfind(']')+1]
        tweets_dict = json.loads(objs)

    tweets_dict = [tweet['tweet'] for tweet in tweets_dict]
    tweets = pd.DataFrame(tweets_dict)
    tweets = tweets.drop(labels=['retweeted', 'source', 'entities', 'display_text_range', 'favorite_count', 'id_str', 'truncated', 'retweet_count', 'favorited', 'lang'], axis=1)
    tweets['created_at'] = pd.to_datetime(tweets['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets['date'] = tweets['created_at'].dt.date

    return tweets.sort_values(by='date')


def get_tweets_by_date(tweets, start=None, end=None):
    if start and end:
        return tweets[(tweets['created_at'] >= start) & (tweets['created_at'] <= end)]
    elif start:
        return tweets[tweets['created_at'] >= start]
    elif end:
        return tweets[tweets['created_at'] <= end]