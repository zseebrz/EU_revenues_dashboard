FROM python:3.6
LABEL maintainer "Zsolt VARGA <zsee@karmafactory.hu>"

ENV PYTHONUNBUFFERED 1

RUN mkdir /dashboard
WORKDIR /dashboard

COPY requirements.txt /dashboard/
RUN pip install -r /dashboard/requirements.txt
COPY ./ /dashboard/
RUN python first_run.py
