#FROM python:3.6-buster
FROM python:3.7.11-slim

LABEL maintainer "Zsolt VARGA <zsee@karmafactory.hu>"
# update all
#RUN apt-get update
#RUN apt-get upgrade -y

RUN pip install --upgrade pip

#try to install pre-requisites for textract

RUN apt update
RUN apt-get update

#RUN apt-get -y install software-properties-common
#RUN apt-add-repository 'deb http://deb.debian.org/debian bullseye unstable main contrib non-free'

#RUN apt-get -y install ghostscript
#RUN apt-get -y install pstotext

RUN apt-get -y install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr
RUN apt-get -y install flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev

#RUN pip install pipenv

ENV PYTHONUNBUFFERED 1

# Create a non-root user
# Please match this with host machine desired uid and gid
RUN groupadd -r --gid 1000 python # 901 for ecadockerhub, 1000 for generic ubuntu 20 installations
RUN useradd --no-log-init --uid 1000 -r -m -g python python # 954 for ecadockerhub, 1000 for generic ubuntu 20 installations
ENV PATH=$PATH:/home/python/.local/bin

#RUN adduser --disabled-password python

# Create the work dir and set permissions as WORKDIR set the permissions as root
RUN mkdir /home/python/app/ && chown -R python:python /home/python/app
ADD . /home/python/app
WORKDIR /home/python/app

USER python

ENV PATH="/home/worker/.local/bin:${PATH}"

#COPY requirements.txt /home/python/app
RUN pip install --user -r /home/python/app/requirements.txt
RUN python -m nltk.downloader punkt
#COPY ./ /home/python/app

COPY --chown=python:python . .

#RUN cd /home/python/app/
#RUN python first_run.py

