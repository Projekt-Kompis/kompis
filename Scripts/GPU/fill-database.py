#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup

import csv
import urllib.request
import re

brands = ["nvidia", "amd", "ati"]
throwawayStrings = [' (SLI Disabled)',' (CrossFire Disabled)']
OEMs = ['zotac','powercolor','asus','pny','sapphire','msi','gigabyte','msi','xfx','igpu']

try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
	print("No connection to Database")
	sys.exit(0)
print("Connection succesfull!")

with open('GPU_UserBenchmarks(1).csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	for row in csv_reader:
		if line_count == 0:
			print(f'Column names are {", ".join(row)}')
			line_count += 1
		else:
			model = row[3]
			if not row[2] or not any(ext in row[2].lower() for ext in brands) or any(ext in model.lower() for ext in OEMs):
				continue
			for string in throwawayStrings:
				model = model.replace(string, "")
			print(f'\nBrand: {row[2]}\nModel: {model}\nuserbenchmark_score: {row[5]}\nuserbenchmark_url: {row[7]}\ntdp:\nfrequency:')
			cursor = connection.cursor()
			sqlIN = "INSERT INTO part (model, type, brand) VALUES (%s, 'gpu', %s) ON DUPLICATE KEY UPDATE model = VALUES(model), brand = VALUES(brand), id=LAST_INSERT_ID(id)"
			sqlVAL = model, row[2]
			cursor.execute(sqlIN, sqlVAL)
			part_id = cursor.lastrowid
			connection.commit()
			cursor = connection.cursor()
			sqlIN = "INSERT INTO part_gpu (userbenchmark_score, userbenchmark_url, tdp, vram, part_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE userbenchmark_url = VALUES(userbenchmark_url), userbenchmark_score = VALUES(userbenchmark_score), id=LAST_INSERT_ID(id)"
			sqlVAL = row[5], row[7], 0, 0, part_id
			cursor.execute(sqlIN, sqlVAL)
			connection.commit()
			line_count += 1
	print(f'Processed {line_count} lines.')

#cursor = connection.cursor()
#sqlIN = "INSERT INTO sbazartest (Name, URL, Description, Price) VALUES (%s, %s, %s, %s)"
#sqlVAL = parsed_json['name'], parsed_json['offers']['url'], parsed_json['description'], parsed_json['offers']['price']
#cursor.execute(sqlIN, sqlVAL)
#connection.commit()