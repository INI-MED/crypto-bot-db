FROM python:3.8-slim-buster

WORKDIR /db_api

COPY requirements.txt .

RUN pip install -r requirements.txt

ADD . .
