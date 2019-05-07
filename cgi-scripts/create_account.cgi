#!/usr/bin/python
import cgi, cgitb
cgitb.enable()
import sys
import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import time
import datetime
import MySQLdb
import hashlib

'''
Allows db access without recreating it each time
'''

#print "Content-type:text/html\r\n\r\n"
db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="creator", passwd="create", db="Cast_Source")
cur = db.cursor()


def handleOutput(value="NO OUTPUT"):
    print "Content-type:text/html\r\n\r\n"
    print "<html>"
    print "<head>"
    print "<title>Results</title>"
    print "</head>"
    print "<body>"
    print "<h2>Results %s</h2>" % value
    print "</body>"
    print "</html>"

def createAccount(username, password, role):
    '''
    Creates an account
    '''
    global cur
    global db
    date = datetime.date.today()
    day = str(date.day)
    if len(day) < 2:
        day = "0" + day
    month = str(date.month)
    if len(month) < 2:
        month = "0" + month
    create_date = str(date.year) + "-" + month + "-" + day
    cur.execute('INSERT INTO Users (user_name, password, create_date, role) values ("%s", "%s", "%s", "%s");' % (username, password, create_date, role))
    db.commit()

def hashPassword(plaintext):
    sha = hashlib.new('SHA256')
    sha.update(str(plaintext))
    return str(sha.hexdigest())


def checkAccountValidity(username):
    '''
    Checks if an account is valid
    Currently just checks if a user is using an already used email address
    '''
    
    db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="retriever", passwd="pull_info", db="Cast_Source")
    #info sourced from https://stackoverflow.com/questions/372885/how-do-i-connect-to-a-mysql-database-in-python
    cur = db.cursor()
    cur.execute('SELECT user_name FROM Users WHERE user_name = "%s"'%(username))
    if len(cur.fetchall()) > 0:
        return False 
    return True

def invalidEntry(errorMessage):
    '''
    The function to handle if a user has incorrectly created an account in any way
    '''
    with open("/var/www/html/create_account.html", "r") as loginPage:    
        print "Content-type:html\r\n\r\n"
        counter = 0
        for line in loginPage:
            if counter == 0:
                counter = 1
                continue
            print line
            parsedLine = line.strip()
            if parsedLine == "</div> <!-- END FORM !-->":
                print '<div class="container"><h5 class="red-text">%s</h5></div><br><br>' %(errorMessage)

def validEntry(cookie):
    '''
    The function to handle if a user has successfully created an account
    attaches a cookie and redirects the user to the update_profile page
    '''
    print cookie 
    print "Location: https://castsource.actor//cgi-bin/load_profile.cgi\r\n\r"
    print ""

def createCookie(user):
    '''
    creates and sets a cookie for user
    '''
    #entry in database made so validity can be checked later
    output = ""    
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
        results = cur.fetchall()

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
    return output 

form = cgi.FieldStorage() 
username = form.getvalue('email')
password = form.getvalue('password')
occupation = form.getvalue('actorOrDirector')
done = False

if not username:
    invalidEntry("User Name must be entered for account creation")
    done = True
elif not password:
    invalidEntry("Password must be entered for account creation")
    done = True
elif not occupation:
    invalidEntry("Role/Occupation must be specified for account creation")
    done = True
if done == False:
    if occupation == 'a':
        occupation = "Actor"
    else:
        occupation = "Director"

    if checkAccountValidity(username):
        createAccount(username, hashPassword(password), occupation)
        cookie = createCookie(username)
        validEntry(cookie)
    else:
        invalidEntry("Issue with account creation, please try a different User Name")
