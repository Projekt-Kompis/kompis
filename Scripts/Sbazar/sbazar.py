#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup
page = requests.get(sys.argv[1])
soup = BeautifulSoup(page.content, 'html.parser')

author_tag = soup.find('a', attrs = {'class' : 'c-seller-info__name c-seller-info__name--link'})
category_tag = soup.find('span', attrs = {'class' : 'p-uw-item__cat-btn__cat'})

jscontent = soup.find(type="application/ld+json")

extractedjs = jscontent.string

#print (extractedjs)
parsed_json = (json.loads(extractedjs))
#print(json.dumps(parsed_json, indent=4, sort_keys=True))

#print("\n\nType:", type(parsed_json))

print("\nName:\n", parsed_json['name'])
print("\nAuthor:\n", author_tag.string)
print("\nCategory:\n", category_tag.string)
print("\nPrice:\n", parsed_json['offers']['price'])
print("\nURL:\n", parsed_json['offers']['url'])
print("\nDescription:\n", parsed_json['description'])

# try:
# 	connection = mysql.connector.connect(host = credentials.dbhost, \
# 	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
# except:
#     print("No connection to Database")
#     sys.exit(0)
# print("Connection succesfull!")

# cursor = connection.cursor()
# sqlIN = "INSERT INTO listing_temp (name, store_url, description, price, author, store) VALUES (%s, %s, %s, %s, %s, 'sbazar') ON DUPLICATE KEY UPDATE name = %s, description = %s, price = %s"
# sqlVAL = parsed_json['name'], parsed_json['offers']['url'].split("-", 1)[0], parsed_json['description'], parsed_json['offers']['price'], str(author_tag.string), parsed_json['name'], parsed_json['description'], parsed_json['offers']['price']
# cursor.execute(sqlIN, sqlVAL)
# connection.commit()