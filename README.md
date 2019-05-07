# cast-source
Michael, Anthony, and Jack's capstone project for the Software Engineering class Spring 2019

Network Topology:
There is a public facing server (EC2) which is using Apache httpd. This server delivers webpages over SSL (whose certificate is supplied by Let's Encrypt).
Suporting the server for storage purposes is an S3 bucket (which was desinged to store files, namely the actor's resumes and headshots) and a database.
The s3 bucket is curently defunct. The database is a mysql databases which stores both profile information (under the table Users) and authentication (cookie) data.
The server and storage methods are an an Amazon VPC (meaning the database can only be accessed from the server and the same for the s3 bucket).

The scripts for the server are cgi scripts run through python. These scripts handle loging in, database access, and parsing html to allow for dynamic changes to the page.
The frontend uses html and css (through materialize). 
