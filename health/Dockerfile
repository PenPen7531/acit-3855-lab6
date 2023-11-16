FROM ubuntu:18.04

LABEL maintainer="jwang536@my.bcit.ca"

RUN apt-get update -y && apt-get install python3 python3-pip -y


COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

CMD ["python3", "app.py"]