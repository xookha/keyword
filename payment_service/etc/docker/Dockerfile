FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD etc/requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD . /code/
