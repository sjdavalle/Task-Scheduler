FROM ubuntu:20.04

RUN apt update \
    && apt install -y \
        python3 \
        python3-pip \
        nano \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3.8 /usr/bin/python

RUN pip install \
    pytest \
    schedule \
    psutil 

WORKDIR /test

#Build the dummy process that is gonna to be launched and stopped
COPY dummy.c /test/
RUN gcc -Wall dummy.c -o dummy

COPY *.py /test/
RUN pytest -x -v