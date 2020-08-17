#!/usr/bin/python3

import os
import time
import re
import logging
import requests
import random
import pyowm
import websocket
import urllib.request
import sys
import subprocess
import json
import discord
import googleapiclient.discovery
import praw
import wikiquote
from dotenv import load_dotenv
from googlesearch import search
from selenium.webdriver import Chrome
from contextlib import closing
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from praw.models import MoreComments


#connect to discord------------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
#connect to reddit-------------------------
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USERNAME = 'joe_chat_bot'
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
reddit = praw.Reddit(user_agent=REDDIT_USER_AGENT,
                     client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
#connect to google-------------------------
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.getenv('YT_API_KEY')

#functions--------------------------------!
#reddit content gatherer-------------------
def reddit_comment_search(text):
    subreddit_list = ['all','gaming','gonewild','videos','pics'] 
    comment_list = []#create empty comment list
    for subreddit in subreddit_list:
        subreddit = reddit.subreddit(subreddit)
        limit = 10 #number top level comments gathered in each submission. by modifying this number we can increase or decrease the amount of comments gathered
        index = 0#create index to add limit to comment gathering. otherwise it takes too long
        for submission in subreddit.search(text,limit=2):#this limit is the number of submissions searched. this number also affects the amount of comments gathered.
            for top_level_comment in submission.comments:
                if isinstance(top_level_comment, MoreComments):#skip over non-top level comments(replies to other comments). the goal is to be somewhat relevant
                    continue
                index += 1 #add to index
                comment_list.append(top_level_comment.body)#add comment bodies to a list of all comments gathered.
                if index == limit:
                    break
    if not comment_list:
        x = generate_random_quote()
        return x
    else:
        answer = random.choice(comment_list)#returns a random comment from the search
        print(answer)#prints to console for logging purposes
        return answer

def yt_video_search(text):#finds a youtube video based on text parameter. 
    query = urllib.parse.quote(text)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    video_id_list = ['123456789SJ_u40yfQdY']#seed it with a video URL in case it can't find one
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        url = vid['href']
        video_id_list.append(url)
    yt_video_url = random.choice(video_id_list)
    yt_video_id = yt_video_url[9:]#filter out first part of link text.
    return yt_video_id

def yt_comment_search(yt_video_id):#pulls a comment from youtube video ID parameter
    comment_list = []#initialize empty list of comments
    youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)
    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=yt_video_id
    )
    try:
        comment_dict = request.execute()#pulls a big dict of comments
    except:
        return 'youtube error - fix me daddy'
    for i in comment_dict['items']:#loop through the items in the comment dict to get just comments
        comment = i['snippet']['topLevelComment']['snippet']['textOriginal']
        comment_list.append(comment)
    yt_comment = random.choice(comment_list)
    print('youtube comment found: '+yt_comment)
    return yt_comment

def yt_comment_generator(text):#combine the youtube video and comment search functions to pull a random YT comment from text
    yt_video_id = yt_video_search(text)
    yt_comment = yt_comment_search(yt_video_id)
    return yt_comment

def google_search(text):#google search
        #query = command.split(' ', 1)[1]#strip the command word out of the query
        print(text)
        for j in search(text, tld="com", num=1, stop=1, pause=2):
            l = j
        final_resp = "My first search result for " + text + ": \n"
        return final_resp + l
    
def generate_asip_quote():
    r = requests.get('http://sunnyquotes.net/q.php?random')
    z = r.json()['sqQuote']
    y = str(z)
    return y

def generate_random_quote():
    quotes = []#create empty quotes list
    for t in wikiquote.random_titles():
        quotes.append(wikiquote.quotes(t))
    quotes.append(generate_asip_quote())
    quotes.append(wikiquote.quotes('King of the Hill (season 2)'))
    return quotes        

def flow_control():#change the name
    #helps keep bot's random chat at a reasonable level
    maxrange = 10   #max range for random calculations. larger number = less frequent random commenting
    x1 = random.randint(1, maxrange)
    x2 = random.randint(1, maxrange)
        #if x1 == x2:
            
    


def generate_response(text):
    textToSearch = re.sub('[^A-Za-z0-9]+', ' ', text)#sanitize input using regex before passing it to any other functions
    if textToSearch == "hi":
        return 'hi'
    elif textToSearch.startswith('find'):
        response = google_search(text)
        return response        
    else:#decide the source of reply from the various sources
        response = []#create a list of final respnses to choose from
        response.append(yt_comment_generator(text))
        response.append(reddit_comment_search(text))
        #every once in a while add some super random stuff
        x1 = random.randint(1, 7)
        x2 = random.randint(1, 7)
        if x1 == x2:
            response.append(generate_random_quote())
        try:
            r = random.choice(response)
            return r[0:140]
        except:
            return generate_random_quote()

#main
if __name__ == "__main__":
    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
    @client.event
    async def on_message(message):
        if message.content.startswith('jb '):
            await message.channel.send(generate_response(message.content[3:]))
        else: #randomly say shit even if nobody mentions JoeBot by the jb prefix
            #super complex random calculation
            x1 = random.randint(1, 7)
            x2 = random.randint(1, 7)
            if x1 == x2:
                print('random chat triggered')
                message.channel.send(generate_response(message.content))
    client.run(TOKEN)
#runs the thing