FROM debian:stable-slim
ADD joebot.py /
ADD .env /
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget unzip python3 curl python3-pip
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update && apt-get upgrade -y
RUN apt-get install -y chromium-driver
ENV DISPLAY=:99
RUN pip3 install --disable-pip-version-check websocket_client
RUN pip3 install  --disable-pip-version-check webdriver-manager
RUN pip3 install --disable-pip-version-check pyowm
RUN pip3 install --disable-pip-version-check slackclient==2.0.0
RUN pip3 install --disable-pip-version-check beautifulsoup4
RUN pip3 install --disable-pip-version-check google
RUN pip3 install --disable-pip-version-check chromedriver
RUN pip3 install --disable-pip-version-check selenium
RUN pip3 install --disable-pip-version-check discord
RUN pip3 install --disable-pip-version-check python-dotenv
RUN pip3 install --disable-pip-version-check praw
#run the bot
CMD [ "python3","-u","./joebot.py" ]