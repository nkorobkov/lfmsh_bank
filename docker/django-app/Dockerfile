FROM python:3
LABEL maintainer="nikkorobk@gmail.com"
WORKDIR /usr/src/django-app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY django-app/. /usr/src/django-app
EXPOSE 8000
CMD uwsgi --http :8000 --module main.wsgi
