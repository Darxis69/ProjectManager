# ProjectManager

# Installing python3 and Django
```
$sudo apt-get install python3
$sudo apt-get install python3-pip
$sudo pip3 install Django
```

# Installing Apache2 Web Server
```
$sudo apt-get install apache2
$sudo apt-get install libapache2-mod-wsgi-py3
```

# Configuring Apache2 Web Server
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

# Running Django Web Server (Developer mode)
```
$sudo python3 manage.py runserver
```