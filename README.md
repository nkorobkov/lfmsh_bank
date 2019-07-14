## LFMSH Bank 2.0
Second version of web application to hold economics game in [Summer Physical and Mathematical School](http://lfmsh.ru/)  
First edition can be found [here](https://github.com/insolia/lfmsh_bank)  

## Installation and running

before any installation, you'll  need  to clone the repo and  install  the requirements.
You  may want to use virtual environment for this process.

###  local startup  instructions

- to deploy test server locally we can only work with django code, so `cd django-app`
- make migrations with:
```bash
  ./manage.py makemigrations
  ./manage.py makemigrations bank
``` 
- apply migrations `  ./manage.py migrate`
- create superuser for admin actions `  ./manage.py createsuperuser`
- populate static tables `  ./manage.py add_static_data`
- prepare users info  and place it in `meta_files/users_data`
- add users  to DB with `  ./manage.py add_users`
this command would print credentials for all users from student and staff  groups.  
It will also create one user with extra privileges called bank_manager. 
- collect static files from different apps to single folder `./manage.py collectstatic`
- run test server  `  ./manage.py runserver`
-  go to  <http://127.0.0.1:8000/bank>  and enter credentials printed in console to test app

### building with docker

build image for local hosting with
`
docker build -t django-bank:0.01  -f ./docker/django-app/Dockerfile .
`
and than run it with 
`docker run -d -p 1234:8000 django-bank:0.01`

you can check bank is working on <http://127.0.0.1:1234/bank/>