FROM ubuntu:20.04

COPY . /root/thesis
WORKDIR /root/thesis

RUN apt-get -qq update && apt-get -qq -y install python3 python3-pip curl figlet
RUN pip install -r requirements

CMD python3 src/main.py
