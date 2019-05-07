#!/usr/bin/python
from common import *


print "Content-type:text/html\r\n\r\n"
def parseData(data):
    '''
    parses the retrieved key/value pair into their database compatible forms
    '''
    sha = hashlib.new("SHA256")
    parsedData = {}
    for key in data:
        parsedKey = key
        parsedValue = data[key]
        if key == 'email':
            parsedKey = 'user_name'
        elif key == 'password':
            sha.update(parsedValue)
            parsedValue = sha.hexdigest()
        elif key == 'pref_name':
            parsedKey = 'preferred_name'
        elif key == 'sex':
            parsedKey = 'gender'
        elif key == 'age':
            parsedKey = 'date_of_birth'
        parsedData[parsedKey] = parsedValue
    return parsedData

def extractInfo(result):
    metaData = {}
    information = result
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


def outputResults(results):
    with open('/var/www/html/search.html') as f:
        for line in f:
            if line.strip() != '<h3>Search results:</h3>':
                print line
            else:
                print line
                for result in results:
                    info = extractInfo(result)
                    print '<div class="card horizontal">'
                    print '<div class="card-stacked">'
                    print '<div class="card-content">'
                    if info['name']:
                        print '<span class"card-title">%s</span>' %info['name']
                    if info['preferred_name']:
                        print '<p>%s</p>' %info['preferred_name']
                    if info['gender']:
                        print '<p>%s</p>' %info['gender']
                    if info['date_of_birth']:
                        print '<p>%s</p>' %str(info['date_of_birth'])
                    if info['region']:
                        print '<p>%s</p>' %info['region']
                    if info['description']:
                        print '<p>%s</p>' %info['description']
                    print '</div>'
                    print '<div class="card-action">'
                    print '<a href="mailto:%s">Send %s an email</a>' %(info['user_name'], info['name'])
                    print '</div></div></div>'


potentialFields = ['name', 'sex', 'age', 'region']

form = cgi.FieldStorage() 
submitionData = {}
for field in potentialFields:
    key = field
    value = form.getvalue(field)
    submitionData[key] = value

parsedData = parseData(submitionData)
query = 'SELECT * FROM Users where '
for field in parsedData:
    if field == 'date_of_birth':
        if parsedData[field] == None:
            continue
        query += '(YEAR(CURDATE()) - YEAR(date_of_birth) > %d AND YEAR(CURDATE()) - YEAR(date_of_birth) < %d) AND '%(int(parsedData[field])-5, int(parsedData[field])+5)
    elif field == 'name':
        if parsedData[field] == None:
            continue
        query += '(LOCATE("%s", name) > 0 OR LOCATE ("%s", preferred_name) > 0) AND '%(parsedData[field], parsedData[field])
    elif field == 'region':
        regions = parsedData[field]
        if regions == None or len(regions) == 0:
            continue
        query += '('
        for i in range(len(regions)):
            query += 'LOCATE("%s", region) > 0 '%(regions[i])
            if i != len(regions) - 1:
                query += 'OR '
        query += ') AND '
    else:
        if parsedData[field] == None:
            continue
        query += '(' + field + ' = "%s") AND '%(parsedData[field])

query = query[:-5] + ' AND role = "Actor"' + ';'

db = MySQLdb.connect(host="cast-source.chsukfmhhaw3.us-east-2.rds.amazonaws.com", user="retriever", passwd="pull_info", db="Cast_Source")
cur = db.cursor()
cur.execute(query)
results = cur.fetchall()
outputResults(results)

