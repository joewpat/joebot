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

#connect to discord------------------------
#from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
#commands----------------------------------
name = "@joebot"
#------------------------------------------

#function time
def yt_comment_lookup(text):#finds a youtube comment based on a search using the text parameter
    textToSearch = re.sub('[^A-Za-z0-9]+', ' ', text)#sanitize input using good ole regex
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    url_list = ['https://www.youtube.com/watch?v=ythwlZ5yceI']
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        url = ('https://www.youtube.com' + vid['href'])
        url_list.append(url)
    yt_video_url = random.choice(url_list)
    #run chromium as background task to pull comments
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    comment_list = []
    print('attempting youtube lookup of search: ', textToSearch)
    try:
        with closing(Chrome(options=chrome_options)) as driver:
            wait = WebDriverWait(driver,10)
            driver.get(yt_video_url)
            for item in range(6): #by increasing the highest range you can get more content
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
    if text == "hi":
        return 'hi'
    elif text.startswith('define'):
        response = dictionary_lookup(text)
        return response
    elif text.startswith('find'):
        response = google_search(text)
        return response        
    else:
        response = yt_comment_lookup(text)
        return response

#main
if __name__ == "__main__":
    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
    @client.event
    async def on_message(message):
        if message.content.startswith('jb '):
            async with message.channel.typing():
                response = await generate_response(message.content[3:])
                await message.channel.send(response)
        elif message.content == 'raise-exception':
            raise discord.DiscordException
    client.run(TOKEN)
#runs the thing
