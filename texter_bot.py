#Importing everything
import os
import classified
from twilio.rest import Client
import praw
import time
import smtplib

#Logging into Twilio (In order to text self)
accountSID = classified.accountSID
authToken = classified.authToken
twilioCli = Client(accountSID, authToken)
myTwilioNumber = classified.myTwilioNumber
myCellPhone = classified.myCellPhone

#Logging into reddit in order to use praw
reddit = praw.Reddit(client_id= classified.client_id,
                     client_secret= classified.client_secret,
                     user_agent= classified.user_agent,
                     username= classified.username,
                     password= classified.password)

#Defining keywords (things to look for in title)
keywords = ["blackwidow", "k70", "snowball", "598", "prime", "[prime]"]

#Making sure we don't repeat submissions in order to prevent spam (using files)
def submissions():
    if not os.path.isfile("cache.txt"):
        cache = []
    with open("cache.txt", "r") as f:
        cache = f.read()
        cache = cache.split("\n")
    return cache

#Making sure we don't repeat submissions in order to prevent spam (using files)
def nsfwsubmissions():
    if not os.path.isfile("nsfwcache.txt"):
        nsfwcache = []
    with open("nsfwcache.txt", "r") as f:
        nsfwcache = f.read()
        nsfwcache = nsfwcache.split("\n")
    return nsfwcache

#Fetches subreddit and posts
def main_bot():
    subreddit = reddit.subreddit("buildapcsales")
    print("Running...")
    for submission in subreddit.stream.submissions():
        process_submission(submission, cache, nsfwcache)

#Looks for submissions and processes them
def process_submission(submission, cache, nsfwcache):
    normalized_title = submission.title.lower()
    for currentWord in keywords:
        if submission.over_18 and submission.id not in nsfwcache:
            print("NSFW Match Found || Post title: " + submission.title + " || Post url (NSFW): " + submission.url + " || comments url: " + submission.shortlink)
            bodyMessage = "NSFW Match Found || Post title: " + submission.title + " || Post url (NSFW): " + submission.url + " || comments url: " + submission.shortlink
            message = twilioCli.messages.create(body=bodyMessage, from_=myTwilioNumber, to=myCellPhone)
            emailU(submission)
            messageU(submission, currentWord)
            cache.append(submission.id)
            with open("cache.txt", "a") as f:
                f.write(submission.id + "\n")
            nsfwcache.append(submission.id)
            with open("nsfwcache.txt", "a") as f:
                f.write(submission.id + "\n")
        if currentWord in normalized_title and submission.id not in cache:
             print("Match Found for \"" + currentWord + "\" || Post title: " + submission.title + " || Post url: " + submission.url + " || comments url: " + submission.shortlink)
             bodyMessage = "Match Found for \"" + currentWord + "\" || Post title: " + submission.title + " || Post url: " + submission.url + " || comments url: " + submission.shortlink
             message = twilioCli.messages.create(body=bodyMessage, from_=myTwilioNumber, to=myCellPhone)
             emailU(submission)
             messageU(submission, currentWord)
             cache.append(submission.id)
             with open("cache.txt", "a") as f:
                 f.write(submission.id + "\n")

#Making it so whenever parameters are met, I get sent an email
def emailU(submission):
    email = smtplib.SMTP('smtp.gmail.com', 587)
    type(email)
    print(email.ehlo())
    print(email.starttls())
    email.login(classified.euser, classified.epass)
    emessage = "Subject: BuildAPcSalesBot ALERT\nSale alert --- " + submission.title + "\nDirect Link --- " + submission.url + "\nComments URL --- " + submission.shortlink
    email.sendmail(classified.euser, classified.euser, emessage)
    email.quit()

#Making it so whenever parameters are met, I get a reddit PM
def messageU(submission, currentWord):
    subject = submission.title
    msg = "Match Found for \"" + currentWord + "\" || Post title: " + submission.title + " || Post url: " + submission.url + " || comments url: " + submission.shortlink
    reddit.redditor(classified.redditor_name).message(subject, msg)

#Endless loop that actually runs the bot
cache = submissions()
nsfwcache = nsfwsubmissions()
startupmessage = twilioCli.messages.create(body= "BOT STARTED UP", from_=myTwilioNumber, to=myCellPhone)
while True:
    main_bot()
    time.sleep(30)




