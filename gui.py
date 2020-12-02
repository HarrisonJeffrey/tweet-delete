import json
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import tweepy
from PIL import ImageTk, Image
from decouple import config
import webbrowser
from tweet_reader import convert_js_file, get_tweets_by_date


class TweetDeleteStart:
    def __init__(self, master):
        consumer_key = config('consumer_key')
        consumer_secret = config('consumer_secret')

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.api = None
        self.redirect_url = None
        self.tweets = None
        self.verify = [False, False]

        master.title("Tweet Delete")
        master.resizable(False, False)

        header_frame = ttk.Frame(master)
        header_frame.pack()

        img = Image.open('Twitter_Logo_Blue.png')
        img = img.resize((100, 100), Image.ANTIALIAS)
        self.twitter_logo = ImageTk.PhotoImage(img)
        master.iconphoto(False, self.twitter_logo)
        ttk.Label(header_frame, image=self.twitter_logo).grid(row=0, column=0, pady=5, padx=5)
        ttk.Label(header_frame, text="Welcome to Tweet Delete!").grid(row=0, column=1, columnspan=3, pady=5, padx=5)

        main_frame = ttk.Frame(master)
        main_frame.pack()

        ttk.Label(main_frame, text="To delete tweets we need two things from you!").grid(row=0, column=0, columnspan=10, pady=1, padx=5)
        ttk.Label(main_frame, text="1) The tweet.js file from your Twitter archive").grid(row=1, column=0, columnspan=10, pady=1, padx=5)
        ttk.Label(main_frame, text="2) Your access token").grid(row=2, column=0, columnspan=10, pady=1, padx=5)
        ttk.Label(main_frame, text="Notice: This app doesn't not store any data, so your twitter archive and access tokens are completely private!", wraplength=350).grid(row=4, column=0, columnspan=10, pady=20, padx=5)
        ttk.Button(main_frame, text='Get access code', command=self.grab_auth).grid(row=5, column=2, pady=10, padx=1)
        self.verifier = tk.StringVar()
        ttk.Label(main_frame, text="Access Code: ").grid(row=5, column=3)
        ttk.Entry(main_frame, width=10, textvariable=self.verifier).grid(row=5, column=4, pady=5, padx=1)

        ttk.Button(main_frame, text="Load tweet.js", command=self.load_file).grid(row=6, column=0, columnspan=10, pady=5, padx=2)
        self.loaded_message = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.loaded_message, wraplength=300).grid(row=7, column=0, columnspan=10)

        self.message = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.message, wraplength=300).grid(row=8, column=0, columnspan=10, pady=5, padx=1)

        ttk.Button(main_frame, text="Continue", command=self.next_page).grid(row=9, column=0, columnspan=10, padx=5, pady=5)

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
            print("hi")


def main():
    root = tk.Tk()
    app = TweetDeleteStart(root)
    root.mainloop()


if __name__ == '__main__':
    main()