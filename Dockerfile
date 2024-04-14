FROM python:3.10-slim

LABEL maintainer="albakov.ruslan@gmail.com"

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
