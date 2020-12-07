#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup
page = requests.get("https://www.sbazar.cz/jiri.kwolek/detail/130074988-rtx-gainward-geforce-3060ti-ghost-oc-edition")
soup = BeautifulSoup(page.content, 'html.parser')

jscontent = soup.find(type="application/ld+json")

extractedjs = jscontent.string

print (extractedjs)
parsed_json = (json.loads(extractedjs))
#print(json.dumps(parsed_json, indent=4, sort_keys=True))

print("\n\nType:", type(parsed_json))

print("\nName:\n", parsed_json['name'])
print("\nPrice:\n", parsed_json['offers']['price'])
print("\nURL:\n", parsed_json['offers']['url'])
print("\nDescription:\n", parsed_json['description'])

try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
    print("No connection to Database")
    sys.exit(0)
print("Connection succesfull!")

cursor = connection.cursor()
sqlIN = "INSERT INTO sbazartest (Name, URL, Description, Price) VALUES (%s, %s, %s, %s)"
sqlVAL = parsed_json['name'], parsed_json['offers']['url'], parsed_json['description'], parsed_json['offers']['price']
cursor.execute(sqlIN, sqlVAL)
connection.commit()