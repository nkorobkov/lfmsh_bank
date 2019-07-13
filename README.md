## LFMSH Bank 2.0
Second version of web application to hold economics game in [Summer Physical and Mathematical School](http://lfmsh.ru/)  
First edition can be found [here](https://github.com/insolia/lfmsh_bank)  


###  local startup  instructions

- clone repo
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

