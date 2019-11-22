## Bank SPMS

Bank is a web application that holds individual accounts of more than 130 users with different permissions. It allows it’s users to issue and transfer money and live within the virtual economic system in the [Summer Physical and Mathematical School](https://ipfran.ru/training/summer-school).

More detailed description of the project, architecture and technologies used can be found on [Bank Project Description Page] (https://nkorobkov.github.io/projects/bank)

## Installation and running

before any installation, you'll  need  to clone the repo and  install  the requirements.
You  may want to use virtual environment for this process.

###  Local startup  instructions

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

### Building with docker

build image for local hosting with

`
docker build -t django-bank:0.01  -f ./docker/django-app/Dockerfile .
`
and then run it with 
`docker run -d -p 1234:8000 django-bank:0.01`

you can check bank is working on <http://127.0.0.1:1234/bank/>

This approach requires you to make migrations and populate tables in advance. Before constructing  the image. 
Alternatively, if image is already constructed, you can log in into running container with  
`docker exec -it <YOUR_CONTAINER_ID> /bin/bash` and exec all the commands needed to populate database from above. 
All the changes in db would be lost after container restart unless you commit them to image. 

### Docker Compose
Alternatively, there is a possibility to launch lfmsh bank in production like mode with real server and db. 

`docker-compose.yml` file contains configuration for deployment of following schema:

![](https://nkorobkov.github.io/assets/bank/deployment-pic.png)


Run `docker-compose up` to see the application stars up with postgres db, nginx server and django app in separate containers.   
All postgress data would be stored in `docker/postgres/volumes` and would persist container restart.   
After first startup, you  will still need to populate tables manually. Log in to uwsgi container   
`docker exec -it lfmsh_bank_uwsgi_1 /bin/bash`   
and run migrations and static data operations from above. 

In current configuration static data is not stored on github. So, to download it you'll still need to collectstatic manually
Run `./django-app/manage.py collectstatic` from host machine, and nginx container will gain access to this  data automatically. 

After this two operations (static collection and db population) you'll be able  to toggle bank on and off with single `docker-compose up/down` command.


### History

This is a second version of Bank application. First version was developed in 2016 and contained in another repo [here](https://github.com/insolia/lfmsh_bank).  