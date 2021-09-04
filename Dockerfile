FROM python:3.6.12

LABEL maintainer "Zsolt VARGA <zsee@karmafactory.hu>"

RUN pip install --upgrade pip
#RUN pip install pipenv

ENV PYTHONUNBUFFERED 1

RUN adduser --disabled-password python

# Create the work dir and set permissions as WORKDIR set the permissions as root
RUN mkdir /home/python/app/ && chown -R python:python /home/python/app
ADD . /home/python/app
WORKDIR /home/python/app

USER python

ENV PATH="/home/worker/.local/bin:${PATH}"

#COPY requirements.txt /home/python/app
RUN pip install --user -r /home/python/app/requirements.txt
#COPY ./ /home/python/app

COPY --chown=python:python . .

#RUN cd /home/python/app/
#RUN python first_run.py

