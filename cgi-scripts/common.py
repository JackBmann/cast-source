'''
The purpose of this file is to store functions that are common to certain cgi scripts

'''
import cgi, cgitb
cgitb.enable()
import sys
import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import datetime
import MySQLdb
import hashlib

#print "Content-type:text/html\r\n\r\n"
def handleDebug(error):
    #print "Content-type:text/html\r\n\r\n"
    print "<html>"
    print "<head>"
    print "<title>Results</title>"
    print "</head>"
    print "<body>"
    print "<h2>Results %s</h2>" % error
    print "</body>"

def isAuthorized(cookieData):
    '''
    checks if a user is authorized based on the cookie
    '''
    db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="retriever", passwd="pull_info", db="Cast_Source")
    cur = db.cursor()
    cur.execute('SELECT * FROM authorized WHERE value = "%s";'%(cookieData['value']))
    results = cur.fetchall()
    '''
    if there is corresponding entry for the cookie value, then the user is authorized
    '''
    if len(results) == 0:
        return False
    else:
        return True

def getMetadata(cookieData):
    '''
    Gets all data from the user's entry in the database based on what the cookie holds in its fields
    '''
    db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="retriever", passwd="pull_info", db="Cast_Source")
    db.commit()
    cur = db.cursor()
    cur.execute('SELECT * FROM Users WHERE user_name = "%s";'%(cookieData['user_name']))
    metaData = {}
    results = cur.fetchall()
    for key in cookieData:
        metaData[key] = cookieData[key] 
    if not len(results) > 0:
        handleDebug("You don't seem to exist. Create an account or contact the admin if this error continues to happen") 
        return metaData
    if len(results) > 1:
        handleDebug("mutliple users exist for the same user_name, contact the admin to resolve this issue")
        return metaData
    information = results[0]
    '''
    this for loop is ugly, but it is ugly here so it won't be somewhere else
    '''
    for i in range(len(information)):
        if i == 0:
            '''
            Don't need id, just skip it
            '''
            continue
        if i == 1:
            metaData["user_name"] = information[i]
        if i == 2:
            '''
            Don't need password, just skip it
            ''' 
            continue
        if i == 3:
            metaData["name"] = information[i]
        if i == 4:
            metaData["preferred_name"] = information[i]
        if i == 5:
            metaData["description"] = information[i]
        if i == 6:
            metaData["gender"] = information[i]
        if i == 7: 
            metaData["date_of_birth"] = information[i]
        if i == 8:
            metaData["region"] = information[i]
        if i == 9:            
            '''
            Don't need create_date, just skip it
            ''' 
            continue
        if i == 11:
            '''
            Don't need last updated
            '''
            continue
        if i == 12:
            metaData["role"] = information[i]
       
    return metaData

def parseLineType(lineType):
    '''
    changes the lineType from its html representation to its database representation for easy retrieval
    NOTE: Database does not have a male or female category
    NOTE: Database does not have a dob category
    '''
    
    if lineType == "email":
        return "user_name"
    if lineType == "email_repeat":
        return "user_name"
    if lineType == "pref_name":
        return "preferred_name"
    if lineType == "dob":
        return "date_of_birth"
    if lineType == "sex":
        return "gender"
    return lineType

def fillFields(cookieData):
    '''
    pre-fills the fields of profile.html with information found in the database
    cookie is a hashmap of potential cookie values
    ''' 
    userData = getMetadata(cookieData)
    #userData = cookieData
    if not isAuthorized(userData):
        handleDebug("Not authorized, please re-login, cookievalue is %s"%(userData['value']))
        return
    with open("/var/www/html/profile.html", "r") as profilePage:
        counter = 0
        for line in profilePage:
            if counter == 0:
                counter = 1
                continue
            parsedLine = line.strip()
            newLine = line
            if len(line) < 6:
                print line
                continue
            if parsedLine[1:6] == "input":
                #if we have an input line, parse and find the place to add the placeholder
                lineID = ""
                lineType = ""
                lineValue = ""
                lineClass = ""
                lineName = ""
                parsedLine = parsedLine.split(" ") 
                for entry in parsedLine:
                    if "id=" in entry:
                        parsedEntry = entry.split("=")
                        lineID = parsedEntry[1]
                        lineID = lineID.strip('"')
                        lineID = parseLineType(lineID)
                    elif "type=" in entry: 
                        parsedEntry = entry.split("=")
                        lineType = parsedEntry[1]
                        lineType = lineType.strip('"')
                    elif "value=" in entry: 
                        parsedEntry = entry.split("=")
                        lineValue = parsedEntry[1]
                        lineValue = lineValue.strip('"') 
                    elif "class=" in entry: 
                        parsedEntry = entry.split("=")
                        lineClass = parsedEntry[1]
                        lineClass = lineClass.strip('"')
                    elif "name=" in entry: 
                        parsedEntry = entry.split("=")
                        lineName = parsedEntry[1]
                        lineName = lineName.strip('"')
                        lineName = parseLineType(lineName)
                if lineType == "radio" and userData[lineName] == lineValue:
                    newLine = newLine[:-2] + 'checked' + newLine[-2:]
                    print newLine
                    continue
                #elif lineClass == "datepicker" and userData[lineID] != None:
                    #newLine = newLine[:-2] + 'data-value="' + str(userData[lineID]) + '"' + newLine[-2:]
                    #print newLine
                    #continue
                elif lineID in userData and userData[lineID] != None:
                    if lineID == "date_of_birth":
                        newLine = newLine[:-2] + 'data-value="' + str(userData[lineID]) + '"' + newLine[-2:]
                        print newLine
                        continue
                    newLine = newLine[:-2] + ' placeholder=' + '"' + userData[lineID] + '"' + newLine[-2:]
                    print newLine
                    continue
                else:
                    print line
                    continue
            elif parsedLine[1:9] == "textarea":
                #handleDebug("IN DERE DOG") 
                lineID = ""
                parsedLine = parsedLine.split(" ") 
                for entry in parsedLine:
                    if "id=" in entry:
                        parsedEntry = entry.split("=")
                        lineID = parsedEntry[1]
                        lineID = lineID.strip('"')
                        lineID = parseLineType(lineID)
                if lineID in userData and userData[lineID] != None:
                    #handleDebug("REALLY IN DERE DOG")
                    newLine = newLine[:-13] + ' placeholder=' + '"' + userData[lineID] + '"' + newLine[-13:]
                    print newLine
                    continue
                else:
                    print line
                    continue

            print line

def retrieveCookieInformation():
    '''
    retrieve information from stored cookies
    
    '''
    returnHash = {}
    if "HTTP_COOKIE" in os.environ:
        cookieData = os.environ["HTTP_COOKIE"]
        parsedData = cookieData.split(";")
        for entry in parsedData:
            splitted = entry.split('=')
            key = splitted[0].strip()
            value = splitted[1].strip()
            returnHash[key] = value
        return returnHash
    else:
        handleDebug("No cookie is present; please enable cookies and re-login")

