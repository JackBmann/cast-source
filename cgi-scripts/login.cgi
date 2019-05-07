#!/usr/bin/python

import cgi, cgitb
cgitb.enable()
import sys
import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import time
import MySQLdb
import hashlib
import datetime
from random import randint

output = ""
def handleOutput(value):
    if value == "LOGIN SUCCESSFUL":
        print output
        print "Location: https://castsource.actor//cgi-bin/load_profile.cgi\r\n\r"
        print ""
    else:
        print "Content-type:text/html\r\n\r\n"
        print "<html>"
        print "<head>"
        print "<title>Results</title>"
        print "</head>"
        print "<body>"
        print "<h2>Results %s</h2>" % value
        print "</body>"
        print "</html>"

def createCookie(user):
    '''
    creates and sets a cookie for user
    '''
    #entry in database made so validity can be checked later
    global output    
    raw_value = time.time() # just a way to get a different value for each cookie to start with
    sha = hashlib.new('SHA256')
    sha.update(str(raw_value))
    cookie_val = sha.hexdigest()
    db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="authenticator", passwd="authenticate", db="Cast_Source")
    cur = db.cursor()
    cur.execute('SELECT * FROM authorized WHERE value = "%s";' %cookie_val)
    results = cur.fetchall()
    while(len(results) > 0):    
        raw_value = randint(0,3000000000)
        sha.update(str(raw-value))
        cookie_val = sha.hexdigest()
        cur.execute('SELECT * FROM authorized WHERE value = "%s";' %cookie_val)
        resutls = cur.fetchall()

    date = datetime.date.today()
    day = str(date.day)
    if len(day) < 2:
        day = "0" + day
    month = str(date.month)
    if len(month) < 2:
        month = "0" + month
    date = str(date.year) + "-" + month + "-" + day
    cur.execute('INSERT INTO authorized (value, user_name, create_date) values("%s", "%s", "%s");'%(cookie_val, user, date))
    db.commit()
    date = datetime.datetime.now()
    date.replace(minute=date.minute + 1 % 60)
    output += "Set-Cookie:value=%s;\r\n"%cookie_val
    output += "Set-Cookie:user_name=%s;\r\n"%user 
    output += "Set-Cookie:Expires = %s;\r\n"%date
    output += "Set-Cookie:Domain = castsource.actor;"
    
def hashPassword(plaintext):
    sha = hashlib.new('SHA256')
    sha.update(str(plaintext))
    return str(sha.hexdigest())

db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="retriever", passwd="pull_info", db="Cast_Source")

#info sourced from https://stackoverflow.com/questions/372885/how-do-i-connect-to-a-mysql-database-in-python


cur = db.cursor()

#get the information passed in from the login page
form = cgi.FieldStorage() 
user_name = form.getvalue('email')
password = form.getvalue('password')
occupation = form.getvalue('actorOrDirector')


error_message = "The & field must be filled out"
if not user_name:
    error_message = "THE EMAIL FIELD MUST BE FILLED OUT"

if not password:
    error_message = "THE PASSWORD FIELD MUST BE FILLED OUT"

if not occupation:
    error_message = "ERROR with the Actor/Director Radio Button"


if '&' not in error_message:
    handleOutput(error_message)
else:
    cur.execute("use Cast_Source;")
    cur.execute("SELECT user_name FROM Users WHERE user_name = '%s' and password = '%s';" % (user_name, hashPassword(password)))
    results = cur.fetchall()
    if len(results) == 0:
        handleOutput("NO MATCH")
    else:
        createCookie(user_name)
        handleOutput("LOGIN SUCCESSFUL")

