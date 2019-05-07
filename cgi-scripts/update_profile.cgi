#!/usr/bin/python
from common import *


print "Content-type:text/html\r\n\r\n"
def parseData(data):
    '''
    parses the retrieved key/value pair into their database compatible forms
    '''
    parsedData = {}
    sha = hashlib.new("SHA256")
    for key in data:
        parsedKey = key
        parsedValue = data[key]
        if parsedValue == None:
            continue
        if key == 'email':
            parsedKey = 'user_name'
        elif key == 'password':
            sha.update(parsedValue)
            parsedValue = sha.hexdigest()
        elif key == 'sex':
            parsedKey = 'gender'
        elif key == 'dob':
            parsedKey = 'date_of_birth'
        parsedData[parsedKey] = parsedValue
    return parsedData

def getUserID(cookieData):
    '''
    Gets the userID for a given user based on your cookies
    '''  
    db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="retriever", passwd="pull_info", db="Cast_Source")
    cur = db.cursor()
    user_name = cookieData['user_name']
    if not user_name:
        handleDebug("NO user_name in cookie_data, login or contact admin")
    cur.execute('SELECT user_id FROM Users where user_name = "%s";'%(user_name))
    results = cur.fetchall()
    if len(results) < 1:
        handleDebug("USER specified does not exist, contact admin")
    elif len(results) > 2:
        hanldeDebug("USER not unique, contact admin")
    return results[0][0]

def updateAccount(parsedData, cookieData):        
    db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="creator", passwd="create", db="Cast_Source")
    cur = db.cursor()
    if not isAuthorized(cookieData):
        handleDebug("NOT AUTHORIZED, RELOG IN")
        return
    userID = getUserID(cookieData)
    query = "UPDATE Users set "
    for field in parsedData:
            value = parsedData[field]
            if field == "region":
                value = "" + parsedData[field][0]
                for i in range(1, len(parsedData[field])):
                    value += ", " + parsedData[field][i]
            query += field + '=' + '"' + value + '"' + ', '
    query = query[:-2]
    query += "WHERE user_id = %d;"%userID
    cur.execute(query)
    db.commit()

potentialFields = ['email', 'password', 'name', 'preferred_name', 'description', 'sex', 'dob', 'region']
submitionData = {}
form = cgi.FieldStorage()
for field in potentialFields:
    key = field
    value = form.getvalue(field)
    submitionData[key] = value
handleDebug(submitionData)
parsedData = parseData(submitionData)
if len(parsedData) == 0:
    print "Location: https://castsource.actor//cgi-bin/load_profile.cgi\r\n\r"
    print ""
else:
    cookieData = retrieveCookieInformation()
    updateAccount(parsedData, cookieData)
    #print ""
    print "Location: https://castsource.actor//cgi-bin/load_profile.cgi\r\n\r"
    print ""
