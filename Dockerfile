FROM golang:1.17rc2-stretch

RUN apt-get update && apt-get -y install -qq --force-yes python python-pip python3-pip golang-go git 

RUN pip install coloredlogs paramiko

WORKDIR /client

COPY . /client

RUN mkdir /share && mkdir /log

CMD python3 main.py