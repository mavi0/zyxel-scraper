FROM python:3

WORKDIR /client

RUN pip install paramiko coloredlogs

COPY . /client

RUN mkdir /share && mkdir /log

CMD [ "python", "./main.py" ]