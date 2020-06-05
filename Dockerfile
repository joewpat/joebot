FROM debian:stable-slim
ADD joebot.py /
ADD .env /
ADD google.json /
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget unzip python3 curl python3-pip
RUN apt-get -y update && apt-get upgrade -y
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
RUN pip3 install --disable-pip-version-check google-api-python-client
#run the bot
CMD [ "python3","-u","./joebot.py" ]