import json
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import tweepy
from PIL import ImageTk, Image
from decouple import config
import webbrowser
from tweet_reader import convert_js_file, get_tweets_by_date
import pandas as pd
import datetime


class TweetDelete(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Tweet Delete")
        self.resizable(False, False)
        self.geometry('320x420')

        img = Image.open('Twitter_Logo_Blue.png')
        img = img.resize((100, 100), Image.ANTIALIAS)
        self.twitter_logo = ImageTk.PhotoImage(img)
        self.iconphoto(False, self.twitter_logo)

        self.tweets = None
        self.api = None
        self.view_tweets = None
        self.view_month = None

        container = tk.Frame(self)
        container.pack()

        self.frames = {}

        for F in (TweetStartPage, TweetMonthsPage, TweetFilterPage, TweetDeletePage):
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
        self.parent = parent

        consumer_key = config('consumer_key')
        consumer_secret = config('consumer_secret')

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.redirect_url = None
        self.verify = [False, False]

        self.twitter_logo = controller.twitter_logo
        ttk.Label(self, image=self.twitter_logo).grid(row=0, column=0, pady=5, padx=5)
        ttk.Label(self, text="Welcome to Tweet Delete!").grid(row=0, column=1, columnspan=3, pady=5, padx=5)

        ttk.Label(self, text="To delete tweets we need two things from you!").grid(row=1, column=0, columnspan=10,
                                                                                   pady=1, padx=5)
        ttk.Label(self, text="1) The tweet.js file from your Twitter archive").grid(row=2, column=0, columnspan=10,
                                                                                    pady=1, padx=5)
        ttk.Label(self, text="2) Your access token").grid(row=3, column=0, columnspan=10, pady=1, padx=10)
        ttk.Label(self,
                  text="Notice: This app doesn't not store any data, so your twitter archive and access tokens are completely private!",
                  wraplength=350).grid(row=5, column=0, columnspan=10, pady=20, padx=5)
        ttk.Button(self, text='Get access code', command=self.grab_auth).grid(row=6, column=0, pady=10, padx=1)
        self.verifier = tk.StringVar()
        ttk.Label(self, text="Access Code: ").grid(row=6, column=2)
        ttk.Entry(self, width=10, textvariable=self.verifier).grid(row=6, column=3, pady=5, padx=1)

        ttk.Button(self, text="Load tweet.js", command=self.load_file).grid(row=7, column=0, pady=5, padx=2)
        self.loaded_message = tk.StringVar()
        ttk.Label(self, textvariable=self.loaded_message, wraplength=200).grid(row=7, column=1, columnspan=7)

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
            self.controller.tweets = convert_js_file(tweets_filepath)
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
            self.controller.api = tweepy.API(self.auth)
            self.message.set('')
            self.verify[1] = True
        except tweepy.TweepError:
            error = 'Error! Failed to get access token.'
            print(error)
            self.message.set(error)
            self.verify[1] = False

    def next_page(self):
        # DELETE AFTER DEBUG
        self.controller.frames[TweetMonthsPage].show_months()
        self.controller.show_frame(TweetMonthsPage)

        # UNCOMMENT AFTER DEBUG
        # self.verify_auth()
        #
        # if False in self.verify:
        #     self.message.set("Something isn't right. Have you loaded your tweets.js archive and verified access?")
        # else:
        #     self.message.set("")
        #     self.controller.show_frame(TweetMonthsPage)


class TweetMonthsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Select a month below to start browsing tweets to delete.", wraplength=350).grid(row=0, column=0, columnspan=10, padx=10, pady=10)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(
                                       scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=1, column=0, columnspan=9)
        self.scrollbar.grid(row=1, column=9, sticky='ns')

    def show_months(self):
        self.controller.geometry('400x360')
        try:
            unique_dates = self.controller.tweets['month_year'].unique().tolist()
            cols = list(range(0, 9, 3))*(len(unique_dates)//3+1)
            for i, date in enumerate(unique_dates):
                tk.Button(self.scrollable_frame, width=15, text=date, command=lambda date=date: self.view_month(date)).grid(row=i//3, column=cols[i], columnspan=3, padx=5, pady=5)
        except TypeError:
            print("Error. Tweets not loaded.")

    def view_month(self, date):
        tweets_month = self.controller.tweets[self.controller.tweets['month_year'] == date]
        self.controller.view_tweets = tweets_month
        self.controller.view_month = date
        self.controller.frames[TweetFilterPage].show_tweets()
        self.controller.show_frame(TweetFilterPage)


class TweetFilterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.message = tk.StringVar()
        self.selected_tweets = None
        ttk.Label(self, textvariable=self.message).grid(row=1, column=0, columnspan=10)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollable_frame = ttk.Frame(self)

        self.build_canvas()

        self.back_button = tk.Button(self, text="Back", command=self.back, width='10').grid(row=2, column=8)

        #TODO also add a button to delete all tweets (with confirmation)
        #TODO make canvas resizable

    def build_canvas(self):
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(
                                       scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set, width=780, height=400)
        self.canvas.grid(row=1, column=0, columnspan=9, pady=10)
        self.scrollbar.grid(row=1, column=10, sticky='ns')

    def show_tweets(self):
        self.controller.geometry('800x500')
        self.controller.resizable(False, True)
        self.scrollable_frame.configure(width=780, height=400)
        ttk.Label(self, text=f"Tweets from {self.controller.view_month}").grid(row=0, column=0, columnspan=10, padx=10, pady=10)
        self.selected_tweets = [tk.IntVar() for x in range(len(self.controller.view_tweets))]
        try:
            for i in range(len(self.controller.view_tweets)):
                tk.Checkbutton(self.scrollable_frame, variable=self.selected_tweets[i]).grid(row=4+i+1, column=0)
                tk.Label(self.scrollable_frame, text=f"{self.controller.view_tweets['day'].iloc[i]} {self.controller.view_tweets['month_year'].iloc[i]}",
                         bg='white', borderwidth=2, relief="ridge").grid(row=4+i+1, column=1)
                tk.Label(self.scrollable_frame, text=self.controller.view_tweets['full_text'].iloc[i], width=93, bg='white',
                         borderwidth=2, relief="ridge", wraplength=650, anchor="w").grid(sticky="W", row=4+i+1, column=2, columnspan=7, padx=5)

            self.canvas.config(scrollregion=self.canvas.bbox("all"))
        except TypeError:
            print("No tweets loaded")

    def grab_tweets(self):
        try:
            page_tweets = (self.page.get() + 1) * 10
            if len(self.controller.tweets) < page_tweets:
                print(page_tweets)
                print(len(self.controller.tweets))
                page_tweets = page_tweets - (len(self.controller.tweets) - page_tweets)
            for i in range(self.page.get(), page_tweets):
                tk.Radiobutton(self, padx=20, variable=self.selected_tweets[i], value=1).grid(row=4+i+1, column=0)
                tk.Label(self, text=self.controller.tweets['created_at'].iloc[i]).grid(row=4+i+1, column=1, columnspan=2)
                tk.Label(self, text=self.controller.tweets['full_text'].iloc[i]).grid(row=4+i+1, column=3, columnspan=7, padx=5)
        except TypeError:
            print("No tweets loaded")

    def back(self):
        self.build_canvas()
        self.controller.geometry('400x360')
        self.controller.show_frame(TweetMonthsPage)


class TweetDeletePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
