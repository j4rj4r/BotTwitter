FROM python:3.8.7
Maintainer j4rj4r

COPY . /App
WORKDIR /App

RUN pip install -r requirements.txt

CMD ["python","-u","/App/main.py"]
