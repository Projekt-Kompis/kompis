#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup
from collections import OrderedDict
from fuzzywuzzy import fuzz
from time import sleep

try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
	print("No connection to Database")
	sys.exit(0)
print("Connection succesfull!")

sql_select_Query = "SELECT part_gpu.part_id, part.model FROM `part` INNER JOIN part_gpu ON part_gpu.part_id = part.id WHERE part.type = 'GPU' AND part_gpu.tdp = '0' AND part_gpu.vram = '0'"
cursor = connection.cursor()
cursor.execute(sql_select_Query)
records = cursor.fetchall()
print("GPUs to update: ", cursor.rowcount)

print("\nUpdating each GPU record")
for row in records:
	model = row[1].replace("-", " ").replace(" (FireGL V)","").replace("S (Super)"," Super")
	print(model)
	response = requests.get("https://www.techpowerup.com/gpu-specs/",params={'ajaxsrch':model})
	soup = BeautifulSoup(response.content, 'html.parser')
	entries = soup.find_all('tr')
	if not entries:
		continue
	header = entries[0].find_all('th', text=True)
	GPUInfoFinal = OrderedDict()
	lastRatio = 0
	for entry in entries:
		GPUInfo = OrderedDict()
		columns = entry.find_all('td')
		if not columns:
			continue
		columnCount = 0
		for column in columns:
			GPUInfo[header[columnCount].text] = column
			columnCount = columnCount + 1
		currentRatio = fuzz.ratio(model, GPUInfo['Product Name'].text)
		if(currentRatio > lastRatio):
			GPUInfoFinal = GPUInfo
	link = GPUInfoFinal['Product Name'].find('a', href=True)
	if not link:
		continue

	sleep(10)
	link = f"https://www.techpowerup.com{link['href']}"
	print(link)
	response = requests.get(link)
	if response.status_code == 429:
		print("Error 429 - Waiting 2 minutes")
		sleep(120)
		response = requests.get(link)
	#print(response.content)
	soup = BeautifulSoup(response.content, 'html.parser')
	try:
		tdp = soup.find("dt", text="TDP").find_next_sibling("dd").text.split(" ")[0]
		if not tdp or tdp == "unknown":
			tdp = 0
		vram = soup.find("dt", text="Memory Size").find_next_sibling("dd").text
	except:
		print("Unable to determine TDP or VRAM, skipping")
		sleep(60)
		continue

	if "GB" in vram:
		vram = int(vram.split(" ")[0])*1024
	elif "MB" in vram:
		vram = int(vram.split(" ")[0])
	else:
		print("Unable to determine VRAM size")
		vram = 0

	cursor = connection.cursor()
	sqlIN = "UPDATE part_gpu SET tdp = %s, vram = %s WHERE part_id = %s"
	print(f'==GPU==\nTDP: {tdp}\nVRAM: {vram}')
	sqlVAL = tdp, vram, row[0]
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()