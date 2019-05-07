#!/usr/bin/python
from common import *

print "Content-type:text/html\r\n\r\n"
cookieValues = retrieveCookieInformation()
fillFields(cookieValues)
