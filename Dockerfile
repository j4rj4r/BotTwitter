FROM python:3.8.7
Maintainer j4rj4r

RUN pip install tweepy PyYAML feedparser
COPY . /App

WORKDIR /App

ENTRYPOINT [ "python" ]

CMD [ "main.py" ]
