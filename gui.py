import json
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import tweepy
from PIL import ImageTk, Image
from decouple import config
import webbrowser
from tweet_reader import convert_js_file, get_tweets_by_date


class TweetDelete(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Tweet Delete")
        self.resizable(False, False)
        self.twitter_logo = ImageTk.PhotoImage(Image.open('Twitter_Logo_Blue.png'))
        self.iconphoto(False, self.twitter_logo)

        container = tk.Frame(self)
        container.pack()

        self.frames = {}

        for F in (TweetStartPage, TweetFilterPage, TweetDeletePage):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(TweetStartPage)

    def show_frame(self, contain):
        frame = self.frames[contain]
        frame.tkraise()


class TweetStartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        consumer_key = config('consumer_key')
        consumer_secret = config('consumer_secret')

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.api = None
        self.redirect_url = None
        self.tweets = None
        self.verify = [False, False]

        img = Image.open('Twitter_Logo_Blue.png')
        img = img.resize((100, 100), Image.ANTIALIAS)
        self.twitter_logo = ImageTk.PhotoImage(img)
        ttk.Label(self, image=self.twitter_logo).grid(row=0, column=0, pady=5, padx=5)
        ttk.Label(self, text="Welcome to Tweet Delete!").grid(row=0, column=1, columnspan=3, pady=5, padx=5)

        ttk.Label(self, text="To delete tweets we need two things from you!").grid(row=1, column=0, columnspan=10, pady=1, padx=5)
        ttk.Label(self, text="1) The tweet.js file from your Twitter archive").grid(row=2, column=0, columnspan=10, pady=1, padx=5)
        ttk.Label(self, text="2) Your access token").grid(row=3, column=0, columnspan=10, pady=1, padx=5)
        ttk.Label(self, text="Notice: This app doesn't not store any data, so your twitter archive and access tokens are completely private!", wraplength=350).grid(row=5, column=0, columnspan=10, pady=20, padx=5)
        ttk.Button(self, text='Get access code', command=self.grab_auth).grid(row=6, column=0, pady=10, padx=1)
        self.verifier = tk.StringVar()
        ttk.Label(self, text="Access Code: ").grid(row=6, column=2)
        ttk.Entry(self, width=10, textvariable=self.verifier).grid(row=6, column=3, pady=5, padx=1)

        ttk.Button(self, text="Load tweet.js", command=self.load_file).grid(row=7, column=0, columnspan=10, pady=5, padx=2)
        self.loaded_message = tk.StringVar()
        ttk.Label(self, textvariable=self.loaded_message, wraplength=300).grid(row=8, column=0, columnspan=10)

        self.message = tk.StringVar()
        ttk.Label(self, textvariable=self.message, wraplength=300).grid(row=9, column=0, columnspan=10, pady=5, padx=1)

        ttk.Button(self, text="Continue", command=self.next_page).grid(row=10, column=0, columnspan=10, padx=5, pady=5)

    def grab_auth(self):
        if self.redirect_url is None:
            try:
                self.redirect_url = self.auth.get_authorization_url()
                self.message.set('')
            except tweepy.TweepError:
                error = 'Error! Failed to get request token.'
                print(error)
                self.message.set(error)

        webbrowser.open(self.redirect_url, new=0, autoraise=True)

    def load_file(self):
        tweets_filepath = askopenfilename(initialdir="C:/", title="Select tweets.js file",
                                          filetypes=(('json files', '*.js'), ('All files', '*')))
        try:
            self.tweets = convert_js_file(tweets_filepath)
            self.message.set('')
            self.loaded_message.set(f'Tweets file at {tweets_filepath} loaded!')
            self.verify[0] = True
        except json.decoder.JSONDecodeError or FileNotFoundError:
            error = "Incorrect file! Did you select the tweets.js file from your archive?"
            print(error)
            self.message.set(error)
            self.verify[0] = False

    def verify_auth(self):
        try:
            self.auth.get_access_token(self.verifier.get())
            self.api = tweepy.API(self.auth)
            self.message.set('')
            self.verify[1] = True
        except tweepy.TweepError:
            error = 'Error! Failed to get access token.'
            print(error)
            self.message.set(error)
            self.verify[1] = False

    def next_page(self):
        self.verify_auth()

        if False in self.verify:
            self.message.set("Something isn't right. Have you loaded your tweets.js archive and verified access?")
        else:
            self.message.set("")
            self.controller.show_frame(TweetFilterPage)


class TweetFilterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        ttk.Label(self, text="test")


class TweetDeletePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
