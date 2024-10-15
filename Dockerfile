FROM python:3.12-slim

WORKDIR /app
RUN apt update && apt -y install gcc libpq-dev

COPY /requirements.txt /
RUN pip install setuptools
RUN pip install -r /requirements.txt --no-cache-dir

COPY . .


