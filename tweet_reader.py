import io
import json
import pandas as pd


# Function to convert tweet.js file into a pandas dataframe, removing redundant columns
def convert_js_file(filepath):
    """Takes a filepath directing to tweet.js archive and returns a pandas dataframe of tweets ordered by date"""
    with io.open(filepath, encoding='utf8') as js_file:
        data = js_file.read()
        objs = data[data.find('['): data.rfind(']')+1]
        tweets_dict = json.loads(objs)

    tweets_dict = [tweet['tweet'] for tweet in tweets_dict]
    tweets = pd.DataFrame(tweets_dict)
    tweets = tweets.drop(labels=['retweeted', 'source', 'entities', 'display_text_range', 'favorite_count', 'id_str', 'truncated', 'retweet_count', 'favorited', 'lang'], axis=1)
    tweets['created_at'] = pd.to_datetime(tweets['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    tweets['day'] = tweets['created_at'].dt.day
    tweets['month_year'] = tweets['created_at'].dt.strftime('%B %Y')

    return tweets.sort_values(by='created_at')


# Return all tweets between two dates (if only start is inputted then return all tweets after, reverse for end)
def get_tweets_by_date(tweets, start=None, end=None):
    """Received dataframe of tweets along with a start and end datetime and returns tweet in the range"""
    if start and end:
        return tweets[(tweets['created_at'] >= start) & (tweets['created_at'] <= end)]
    elif start:
        return tweets[tweets['created_at'] >= start]
    elif end:
        return tweets[tweets['created_at'] <= end]


# Function that converts text file containing profanities tagged by google into a list and return it
def grab_bad_words():
    """Collects a list of bad words from textfile"""
    with open('google_profanity_words.txt') as f:
        bad_words = f.readlines()
    bad_words = [word.strip() for word in bad_words]

    return bad_words
