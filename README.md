# public_transport

You will need to create some extra files

credentials.txt
if you asked De Lijn for access to their data

----

dblogin.py

where you put your database login details:

import postgresql

db = postgresql.open('pq://username:password@url:port/dbinstance')

----

For the psql commands in the .sh files to work, you'll also need a pgpass file in your home folder:

~/.pgpass

url:port:dbinstance:username:password

----

You will need to start a virtualenv and install the following packages in it:

pip install django pytz requests urllib ftplib

for py_postgresql refer to http://python.projects.pgfoundry.org/

----
