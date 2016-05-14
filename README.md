# ProjectManager

# Install notes

## Installing python3 and Django
```
$sudo apt-get install python3
$sudo apt-get install python3-pip
$sudo pip3 install Django
$sudo pip3 install django-bootstrap3
$sudo pip3 install django-jquery
```

## Installing PostgreSQL
```
$sudo apt-get install postgresql
$sudo apt-get install libpq-dev
$sudo pip3 install psycopg2
```

## Configuring PostgreSQL
Set postgres password
```
$sudo -u postgres psql
postgres=# \password postgres
Enter new password:
Enter it again:
postgres=# \q
```

Create project_manager database
```
$sudo -u postgres psql
postgres=# CREATE DATABASE "project_manager" WITH OWNER "postgres" ENCODING 'UTF-8';
postgres=# \q
```

## Configure Application settings
Edit {PROJECT_DIR}/ProjectManager/settings.py. Set database password in
```
DATABASES = {
    'default': {
        ...
        ...
        'PASSWORD': '<mypassword>',
        ...
        ...
    }
}
```

## Create database schema
```
$sudo python3 manage.py makemigrations
$sudo python3 manage.py migrate
```

# Running instructions

## Running Django Web Server (Developer mode)
```
$sudo python3 manage.py runserver
```

# Production environment notes

## Installing Apache2 Web Server
```
$sudo apt-get install apache2
$sudo apt-get install libapache2-mod-wsgi-py3
```

## Configuring Apache2 Web Server
Enable mod_wsgi:
```
$sudo a2enmod wsgi
```

Edit /etc/apache2/apache2.conf file and add the following:
```flow
WSGIScriptAlias / /var/www/ProjectManager/ProjectManager/wsgi.py
WSGIPythonPath /var/www/ProjectManager

<Directory /var/www/ProjectManager>
    <Files wsgi.py>
        Allow from all
        Order deny,allow
    </Files>
</Directory>
```

## Deployment to production
Copy {PROJECT_DIR} to directory /var/www/

## Example configuration of settings.py
```
DEBUG = False
ALLOWED_HOSTS = ["localhost", "www.somehost.com"]
```

## Restart apache
```
$sudo service apache2 restart
```
