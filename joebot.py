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
import praw
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
#commands----------------------------------
name = "@joebot"
#------------------------------------------

#functions---------------------------------
#reddit content gatherer-------------------
def reddit_comment_search(text):
    subreddit = reddit.subreddit("all")#use subreddit 'all' to cast a wide net
    comment_list = []#create empty comment list
    limit = 15 #by modifying this number we can increase or decrease the amount of comments gathered
    index = 0#create index to add limit to comment gathering. otherwise it takes too long
    for submission in subreddit.search(text,limit=3):
      for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):#skip over non-top level comments. the goal is to be somewhat relevant
            continue
        index += 1 #add to index
        comment_list.append(top_level_comment.body)#add comment bodies to a huge list of random comments
        if index == limit:
            break
    answer = random.choice(comment_list)#returns a random comment from the search
    print(answer)#prints to console for logging purposes
    return answer


def yt_comment_lookup(text):#finds a youtube comment based on a search using the text parameter
    query = urllib.parse.quote(text)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    url_list = ['https://www.youtube.com/watch?v=ythwlZ5yceI']#set a default video as the base url list for youtube in case nothing gets found
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        url = ('https://www.youtube.com' + vid['href'])
        url_list.append(url)
    yt_video_url = random.choice(url_list)
    #run chromium as background task to pull comments
    chrome_options = Options()  
    chrome_options.add_argument("--headless")#opens chrome with no gui
    chrome_options.add_argument("--no-sandbox")#not sure why I need this
    chrome_options.add_argument("--disable-dev-shm-usage")#or this
    comment_list = []#create empty comment list to add things to
    print('attempting youtube lookup of search: ', text)
    try:
        with closing(Chrome(options=chrome_options)) as driver:
            wait = WebDriverWait(driver,10)
            driver.get(yt_video_url)
            for item in range(3): #wait time for comment finding. larger numbers slow the bot down
                wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
                print(item+1, "seconds waited for content")
                time.sleep(1)
            print('page content loaded')
            print('attempting to load comments...')
            n = 0
            for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#comment #content-text"))):
                n+=1
                comment_list.append(comment.text)
            print(n, 'comments found via CSS selector')
            t = random.choice(comment_list)
            print(t)
        return t
    except:
        t = generate_asip_quote()
        return t        

def generate_meme():
    pass




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

def generate_response(text):
    textToSearch = re.sub('[^A-Za-z0-9]+', ' ', text)#sanitize input using regex
    if textToSearch == "hi":
        return 'hi'
    elif textToSearch.startswith('find'):
        response = google_search(text)
        return response        
    else:
        #decide if it will be reddit or youtube
        response = []#create a list of final respnses to choose from
        #response.append(yt_comment_lookup(text)) disabled youtube until I can quickify it
        response.append(reddit_comment_search(text))
        response.append(generate_asip_quote())
        return random.choice(response)

#main
if __name__ == "__main__":
    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
    @client.event
    async def on_message(message):
        if message.content.startswith('jb '):
            async with message.channel.typing():
                response = generate_response(message.content[3:])
                await message.channel.send(response)
        elif message.content == 'raise-exception':
            raise discord.DiscordException
    client.run(TOKEN)
#runs the thing