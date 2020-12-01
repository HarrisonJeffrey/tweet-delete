from decouple import config
import webbrowser
import tweepy
from tweet_reader import convert_js_file, get_tweets_by_date


def tweepy_auth():
    consumer_key = config('consumer_key')
    consumer_secret = config('consumer_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get request token.')

    webbrowser.open(redirect_url, new=0, autoraise=True)
    verifier = input('Verifier: ')

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    api = tweepy.API(auth)
    return api


def main():
    api = tweepy_auth()

    filepath = 'tweet.js'
    tweets = convert_js_file(filepath)

    # id = '1333848716311224320'
    # api.destroy_status(id)


if __name__ == '__main__':
    main()