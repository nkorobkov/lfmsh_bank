FROM python:3
MAINTAINER nikkorobk
COPY django-app/. /usr/src/django-app
WORKDIR /usr/src/django-app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD uwsgi --http :8000 --module main.wsgi
